"""
Test DNS resolution for Supabase
"""
import socket

hosts_to_test = [
    "db.sgjbvjmeqrucofdklmec.supabase.co",
    "aws-0-us-east-1.pooler.supabase.com",
]

for host in hosts_to_test:
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ {host} -> {ip}")
    except socket.gaierror as e:
        print(f"❌ {host} -> Failed: {e}")

# Also test with the project ref
print("\nTrying alternative formats:")
alternatives = [
    "sgjbvjmeqrucofdklmec.supabase.co",
    "aws-0-us-west-1.pooler.supabase.com",
]

for host in alternatives:
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ {host} -> {ip}")
    except socket.gaierror as e:
        print(f"❌ {host} -> Failed: {e}")
