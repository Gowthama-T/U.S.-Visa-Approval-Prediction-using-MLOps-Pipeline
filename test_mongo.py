from pymongo import MongoClient

# Paste your NEW connection string here after updating password
uri = "mongodb+srv://GowthamKullu:Gowtham2025@cluster0.rt0zh1e.mongodb.net/?appName=Cluster0"

try:
    print("🔄 Trying to connect to MongoDB...")
    client = MongoClient(uri)

    # Check server info and list databases
    print("🎉 Connected to MongoDB Successfully!")
    print("📁 Available Databases:", client.list_database_names())

except Exception as e:
    print("❌ Error connecting to MongoDB:")
    print(e)
