
use taxidb;

db.createCollection("taxi_registration");
db.createCollection("taxi");
db.createCollection("taxi_history");
db.createCollection("user");
db.createCollection("user_history");

db.taxi.createIndex({location: "2dsphere"});
db.taxi.createIndex( { email: 1 }, { unique: true } )
db.user.createIndex( { email: 1 }, { unique: true } )

// db.taxi.find( { 
//     location: { 
//        $near: { 
//            $geometry: { 
//                type: "Point", coordinates: [78.0521, 13.409] 
//            }, 
//            $minDistance: 0, 
//            $maxDistance: 5000 
//        } 
//    } 
//} );
