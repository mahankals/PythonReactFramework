"""
Create admin user command.

Usage:
    Interactive mode:
        docker compose exec -it backend python -m app.create_admin

    Direct mode:
        docker compose exec backend python -m app.create_admin \\
            --email admin@example.com \\
            --password SecurePass123 \\
            --first-name John \\
            --last-name Doe
"""
import argparse
import asyncio
import getpass
from passlib.context import CryptContext
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.rbac import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin(
    email: str,
    password: str,
    first_name: str,
    last_name: str
):
    """Create a new super admin user with superadmin role."""
    async with AsyncSessionLocal() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Error: User with email '{email}' already exists.")
            if existing.is_superadmin:
                print("This user is already a super admin.")
            else:
                print("Promoting user to super admin...")
                existing.is_superadmin = True
                # Get and assign superadmin role
                result = await db.execute(select(Role).where(Role.name == "superadmin"))
                superadmin_role = result.scalar_one_or_none()
                if superadmin_role and superadmin_role not in existing.roles:
                    existing.roles.append(superadmin_role)
                await db.commit()
                print(f"User '{email}' is now a super admin.")
            return

        # Get superadmin role
        result = await db.execute(select(Role).where(Role.name == "superadmin"))
        superadmin_role = result.scalar_one_or_none()

        # Create new super admin user
        user = User(
            email=email,
            password_hash=pwd_context.hash(password),
            first_name=first_name,
            last_name=last_name,
            is_superadmin=True,
            is_active=True,
            email_verified=True,
            roles=[superadmin_role] if superadmin_role else [],
        )
        db.add(user)
        await db.commit()
        print(f"Super admin user created: {email}")


def get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()

    if not value and default:
        return default
    if not value and required:
        print("This field is required.")
        return get_input(prompt.replace(": ", "").replace(f" [{default}]", ""), default, required)
    return value


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a superadmin user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    docker compose exec -it backend python -m app.create_admin

  Direct mode:
    docker compose exec backend python -m app.create_admin \\
        --email admin@example.com \\
        --password SecurePass123 \\
        --first-name John \\
        --last-name Doe
        """
    )
    parser.add_argument("--email", "-e", help="Admin email address")
    parser.add_argument("--password", "-p", help="Admin password (min 6 chars)")
    parser.add_argument("--first-name", "-f", help="First name")
    parser.add_argument("--last-name", "-l", help="Last name")
    return parser.parse_args()


async def main():
    args = parse_args()

    print("=" * 50)
    print("Create Admin User")
    print("=" * 50)
    print()

    # Check if all args provided (direct mode)
    if args.email and args.password and args.first_name and args.last_name:
        email = args.email
        password = args.password
        first_name = args.first_name
        last_name = args.last_name
        print(f"Creating admin: {email} ({first_name} {last_name})")
    else:
        # Interactive mode
        print("Enter admin user details:")
        print()

        email = get_input("Email", args.email)
        first_name = get_input("First Name", args.first_name)
        last_name = get_input("Last Name", args.last_name)

        # Password input (hidden)
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 6:
                print("Password must be at least 6 characters.")
                continue
            password_confirm = getpass.getpass("Confirm Password: ")
            if password != password_confirm:
                print("Passwords do not match. Try again.")
                continue
            break

    print()
    await create_admin(email, password, first_name, last_name)


if __name__ == "__main__":
    asyncio.run(main())
