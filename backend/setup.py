from setuptools import setup, find_packages

setup(
    name="email-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "python-jose[cryptography]",
        "python-multipart",
        "python-dotenv",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "alembic",
    ],
) 