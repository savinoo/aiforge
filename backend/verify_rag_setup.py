#!/usr/bin/env python3
"""
RAG Setup Verification Script
Checks that all components are correctly installed and configured.
"""

import sys
from pathlib import Path


def check_imports():
    """Verify all required imports work."""
    print("🔍 Checking Python imports...")

    required_modules = [
        ("fastapi", "FastAPI"),
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("supabase", "Supabase"),
        ("pydantic", "Pydantic"),
    ]

    failed = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name}: {e}")
            failed.append(name)

    if failed:
        print(f"\n⚠️  Missing dependencies: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False

    return True


def check_rag_modules():
    """Verify RAG modules can be imported."""
    print("\n🔍 Checking RAG modules...")

    try:
        from app.services.rag import (
            rag_config,
            ingestion_service,
            chunking_service,
            embedding_service,
            vectorstore,
            retriever,
            rag_chat,
        )
        print("   ✅ All RAG services imported successfully")

        # Verify config
        assert rag_config.chunk_size > 0
        assert rag_config.embedding_model == "text-embedding-3-small"
        print("   ✅ Configuration validated")

        return True

    except Exception as e:
        print(f"   ❌ Failed to import RAG modules: {e}")
        return False


def check_api_routes():
    """Verify API routes are registered."""
    print("\n🔍 Checking API routes...")

    try:
        from app.api.v1.rag import router

        # Check routes exist
        routes = [r.path for r in router.routes]
        expected = [
            "/rag/ingest",
            "/rag/ingest-url",
            "/rag/chat",
            "/rag/search",
            "/rag/documents",
            "/rag/documents/{document_id}",
            "/rag/config",
        ]

        for route in expected:
            if route in routes:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ Missing route: {route}")
                return False

        return True

    except Exception as e:
        print(f"   ❌ Failed to load API routes: {e}")
        return False


def check_files():
    """Verify all required files exist."""
    print("\n🔍 Checking files...")

    base = Path(__file__).parent

    required_files = [
        "app/services/rag/__init__.py",
        "app/services/rag/config.py",
        "app/services/rag/prompts.py",
        "app/services/rag/ingestion.py",
        "app/services/rag/chunking.py",
        "app/services/rag/embeddings.py",
        "app/services/rag/vectorstore.py",
        "app/services/rag/retriever.py",
        "app/services/rag/chat.py",
        "app/api/v1/rag.py",
        "migrations/001_setup_rag.sql",
        "QUICKSTART_RAG.md",
        "RAG_IMPLEMENTATION_SUMMARY.md",
        "app/services/rag/README.md",
    ]

    missing = []
    for file_path in required_files:
        full_path = base / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            missing.append(file_path)

    if missing:
        print(f"\n⚠️  Missing files: {len(missing)}")
        return False

    return True


def check_environment():
    """Check environment configuration."""
    print("\n🔍 Checking environment...")

    try:
        from app.core.config import settings

        # Check required settings
        checks = [
            ("OPENAI_API_KEY", settings.openai_api_key),
            ("SUPABASE_URL", settings.supabase_url),
            ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
        ]

        missing = []
        for name, value in checks:
            if value and value != "placeholder":
                print(f"   ✅ {name} configured")
            else:
                print(f"   ⚠️  {name} not configured (required for production)")
                missing.append(name)

        if missing:
            print("\n💡 Set these in .env file:")
            for name in missing:
                print(f"   {name}=your_value_here")

        return True

    except Exception as e:
        print(f"   ❌ Failed to load settings: {e}")
        return False


def check_database_migration():
    """Check database migration file."""
    print("\n🔍 Checking database migration...")

    migration_file = Path(__file__).parent / "migrations" / "001_setup_rag.sql"

    if not migration_file.exists():
        print("   ❌ Migration file not found")
        return False

    content = migration_file.read_text()

    required_elements = [
        "create extension if not exists vector",
        "create table documents",
        "create table document_chunks",
        "create index",
        "alter table documents enable row level security",
        "create or replace function match_document_chunks",
    ]

    for element in required_elements:
        if element in content:
            print(f"   ✅ {element}")
        else:
            print(f"   ❌ Missing: {element}")
            return False

    print("\n   📋 Next step: Run this SQL in Supabase SQL Editor")
    print(f"      File: {migration_file}")

    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("RAG Setup Verification")
    print("=" * 60)

    checks = [
        ("Python Imports", check_imports),
        ("RAG Modules", check_rag_modules),
        ("API Routes", check_api_routes),
        ("Files", check_files),
        ("Environment", check_environment),
        ("Database Migration", check_database_migration),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! Your RAG system is ready.")
        print("\n📚 Next steps:")
        print("   1. Run migration: migrations/001_setup_rag.sql in Supabase")
        print("   2. Start server: uvicorn app.main:app --reload")
        print("   3. Test API: See QUICKSTART_RAG.md")
        return 0
    else:
        print("\n⚠️  Some checks failed. Fix the issues above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
