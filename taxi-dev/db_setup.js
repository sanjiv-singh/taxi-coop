
use taxidb;

db.ride.drop();
db.user.drop();
db.taxi.drop();
db.taxi_history.drop();

db.createCollection("ride");
db.createCollection("user");
db.createCollection("taxi");
db.createCollection("taxi_history");

db.user.createIndex( { email: 1 }, { unique: true } )
db.taxi.createIndex({location: "2dsphere"});
db.taxi.createIndex( { email: 1 }, { unique: true } )

