#!/bin/bash
set -e

# Start mongod in the background
mongod --replSet rs0 --bind_ip_all --port 27017 &

# Wait for mongod to be ready to accept connections
until mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  echo "Waiting for MongoDB to start..."
  sleep 1
done

# Run replica set initiation logic (idempotent)
mongosh --eval "
  try {
    rs.status();
  } catch(e) {
    rs.initiate({
        _id: 'rs0',
        members: [{ _id: 0, host: 'mongodb:27017' }]
    });
  }
"

# Wait on mongod process to keep container running
wait
