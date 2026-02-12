-- Migration: Setup RAG tables and functions
-- Description: Creates documents and document_chunks tables with pgvector support
-- Created: 2024-02-12
-- Run this in Supabase SQL Editor

-- ============================================================================
-- 1. Enable pgvector extension
-- ============================================================================
create extension if not exists vector;

-- ============================================================================
-- 2. Create documents table
-- ============================================================================
create table if not exists documents (
    id uuid default gen_random_uuid() primary key,
    tenant_id uuid not null,
    name text not null,
    source text,
    metadata jsonb default '{}',
    created_at timestamptz default now()
);

-- ============================================================================
-- 3. Create document_chunks table with embeddings
-- ============================================================================
create table if not exists document_chunks (
    id uuid default gen_random_uuid() primary key,
    document_id uuid references documents(id) on delete cascade,
    tenant_id uuid not null,
    content text not null,
    metadata jsonb default '{}',
    embedding vector(1536),
    created_at timestamptz default now()
);

-- ============================================================================
-- 4. Create indexes for performance
-- ============================================================================

-- Vector similarity search index (IVFFlat for fast approximate search)
create index if not exists document_chunks_embedding_idx
    on document_chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- Tenant filtering indexes
create index if not exists document_chunks_tenant_id_idx
    on document_chunks (tenant_id);

create index if not exists document_chunks_document_id_idx
    on document_chunks (document_id);

create index if not exists documents_tenant_id_idx
    on documents (tenant_id);

-- Timestamp index for sorting
create index if not exists documents_created_at_idx
    on documents (created_at desc);

-- ============================================================================
-- 5. Enable Row Level Security (RLS)
-- ============================================================================

alter table documents enable row level security;
alter table document_chunks enable row level security;

-- ============================================================================
-- 6. RLS Policies for documents table
-- ============================================================================

-- Users can view their own documents
create policy "Users can view their own documents"
    on documents for select
    using (auth.uid() = tenant_id);

-- Users can insert their own documents
create policy "Users can insert their own documents"
    on documents for insert
    with check (auth.uid() = tenant_id);

-- Users can update their own documents
create policy "Users can update their own documents"
    on documents for update
    using (auth.uid() = tenant_id);

-- Users can delete their own documents
create policy "Users can delete their own documents"
    on documents for delete
    using (auth.uid() = tenant_id);

-- ============================================================================
-- 7. RLS Policies for document_chunks table
-- ============================================================================

-- Users can view their own chunks
create policy "Users can view their own chunks"
    on document_chunks for select
    using (auth.uid() = tenant_id);

-- Users can insert their own chunks
create policy "Users can insert their own chunks"
    on document_chunks for insert
    with check (auth.uid() = tenant_id);

-- Users can update their own chunks
create policy "Users can update their own chunks"
    on document_chunks for update
    using (auth.uid() = tenant_id);

-- Users can delete their own chunks
create policy "Users can delete their own chunks"
    on document_chunks for delete
    using (auth.uid() = tenant_id);

-- ============================================================================
-- 8. Create similarity search function
-- ============================================================================

create or replace function match_document_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter_tenant_id uuid,
    filter_document_ids uuid[] default null
)
returns table (
    id uuid,
    document_id uuid,
    tenant_id uuid,
    content text,
    metadata jsonb,
    similarity float
)
language sql stable
as $$
    select
        document_chunks.id,
        document_chunks.document_id,
        document_chunks.tenant_id,
        document_chunks.content,
        document_chunks.metadata,
        1 - (document_chunks.embedding <=> query_embedding) as similarity
    from document_chunks
    where
        document_chunks.tenant_id = filter_tenant_id
        and (filter_document_ids is null or document_chunks.document_id = any(filter_document_ids))
        and 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
    order by similarity desc
    limit match_count;
$$;

-- ============================================================================
-- 9. Create helper functions
-- ============================================================================

-- Function to get document stats
create or replace function get_document_stats(doc_id uuid)
returns table (
    document_id uuid,
    chunk_count bigint,
    total_characters bigint,
    avg_chunk_size numeric
)
language sql stable
as $$
    select
        doc_id,
        count(*) as chunk_count,
        sum(length(content)) as total_characters,
        round(avg(length(content)), 2) as avg_chunk_size
    from document_chunks
    where document_id = doc_id
    group by document_id;
$$;

-- Function to get tenant storage usage
create or replace function get_tenant_storage_stats(tenant_uuid uuid)
returns table (
    tenant_id uuid,
    document_count bigint,
    chunk_count bigint,
    total_characters bigint
)
language sql stable
as $$
    select
        tenant_uuid,
        count(distinct d.id) as document_count,
        count(c.id) as chunk_count,
        coalesce(sum(length(c.content)), 0) as total_characters
    from documents d
    left join document_chunks c on d.id = c.document_id
    where d.tenant_id = tenant_uuid
    group by tenant_uuid;
$$;

-- ============================================================================
-- 10. Comments for documentation
-- ============================================================================

comment on table documents is 'Stores document metadata for RAG system';
comment on table document_chunks is 'Stores document chunks with embeddings for semantic search';
comment on column document_chunks.embedding is 'Vector embedding (1536 dimensions from text-embedding-3-small)';
comment on function match_document_chunks is 'Performs cosine similarity search on document chunks with tenant filtering';

-- ============================================================================
-- Migration complete!
-- ============================================================================

-- Verify tables exist
do $$
begin
    if exists (select from information_schema.tables where table_name = 'documents') then
        raise notice 'SUCCESS: documents table created';
    else
        raise exception 'ERROR: documents table not found';
    end if;

    if exists (select from information_schema.tables where table_name = 'document_chunks') then
        raise notice 'SUCCESS: document_chunks table created';
    else
        raise exception 'ERROR: document_chunks table not found';
    end if;

    raise notice '✅ RAG migration completed successfully!';
end $$;
