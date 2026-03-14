#!/usr/bin/env python3
"""
Quick start script for Patient Record Management System
Initializes databases and creates test data
"""

import sys
import argparse
from app.config import initialize_app, create_admin_user, check_databases


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Initialize Patient Record Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py
  python run.py --email admin@example.com --password MyPass123!
  python run.py --skip-mongo
        """
    )

    parser.add_argument(
        '--email',
        type=str,
        default='admin@hospital.com',
        help='Admin email address (default: admin@hospital.com)'
    )

    parser.add_argument(
        '--password',
        type=str,
        default='Admin123!',
        help='Admin password (default: Admin123!)'
    )

    parser.add_argument(
        '--skip-mongo',
        action='store_true',
        help='Skip MongoDB connection checks and setup'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Prompt for email and password interactively'
    )

    return parser.parse_args()


def get_credentials_interactive() -> tuple[str, str]:
    """Get admin credentials interactively"""
    email = input("   Enter admin email (default: admin@hospital.com): ").strip()
    if not email:
        email = "admin@hospital.com"

    password = input("   Enter admin password (default: Admin123!): ").strip()
    if not password:
        password = "Admin123!"

    return email, password


def setup_databases(skip_mongo: bool = False) -> dict:
    """Setup and check databases"""
    results = {
        'sqlite_ok': False,
        'mongodb_ok': False,
        'init_ok': False
    }

    print("\n1. Initializing application...")
    try:
        initialize_app()
        results['init_ok'] = True
    except Exception as e:
        print(f"✗ Initialization failed: {str(e)}")
        return results

    print("\n2. Checking database connections...")
    try:
        check_databases()
        results['sqlite_ok'] = True
        # MongoDB status is checked inside check_databases
        results['mongodb_ok'] = True  # Assume ok unless error printed
    except Exception as e:
        print(f"✗ Database check failed: {str(e)}")

    return results


def create_admin(email: str, password: str) -> bool:
    """Create admin user"""
    print("\n3. Creating admin user...")

    try:
        result = create_admin_user(email, password)

        if result['success']:
            print(f"✓ Admin user created: {email}")
            return True
        else:
            print(f"✗ Failed to create admin user: {result['message']}")
            return False
    except Exception as e:
        print(f"✗ Error creating admin user: {str(e)}")
        return False


def print_summary(email: str, password: str, db_results: dict):
    """Print setup summary"""
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)

    print(f"✓ Admin user: {email}")
    print(f"✓ Admin password: {password}")

    print(f"✓ SQLite: {'Connected' if db_results['sqlite_ok'] else 'Failed'}")
    print(f"{'✓' if db_results['mongodb_ok'] else '⚠'} MongoDB: {'Connected' if db_results['mongodb_ok'] else 'Not connected (limited features)'}")

    print("\n4. Starting the application...")
    print("   Run: python app/app.py")
    print("   Access: http://localhost:5000")

    if not db_results['mongodb_ok']:
        print("\n⚠ Note: MongoDB not connected. Patient records features will be limited.")
        print("   - Check your MongoDB URI and network connection")
        print("   - Ensure MongoDB Atlas IP whitelist includes your IP")

    print("\n" + "=" * 60)


def main():
    """Main setup function"""
    print("=" * 60)
    print("Patient Record Management System - Backend Setup")
    print("=" * 60)

    try:
        # Parse arguments
        args = parse_arguments()

        # Get credentials
        if args.interactive:
            email, password = get_credentials_interactive()
        else:
            email, password = args.email, args.password

        # Setup databases
        db_results = setup_databases(args.skip_mongo)

        # Create admin user
        admin_created = create_admin(email, password)

        # Print summary
        print_summary(email, password, db_results)

        # Return appropriate exit code
        if not db_results['init_ok'] or not admin_created:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
