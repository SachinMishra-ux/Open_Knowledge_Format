from google_okf import MongoDBProducer, write_bundle

# 1. Initialize MongoDB Producer
producer = MongoDBProducer(
    connection_uri="mongodb+srv://sachin319566_db_user:0UaX8ONUzR6TNtIh@upicluster.trdgo4v.mongodb.net/?appName=UPICluster",
    database_name="upi_db",
    output_prefix="database/collections"
)

# 2. Extract and generate OKF concepts
concepts = producer.produce()

# 3. Save to bundle
write_bundle("mongodb_bundle", concepts)