import express from 'express';
import dotenv from 'dotenv';

// now the imports for database connection 
import { MongoClient, ServerApiVersion } from 'mongodb';

dotenv.config()

const app = express()

const client = new MongoClient(process.env.MONGODB_URI, {
    maxPoolSize: 10,
    serverApi:{
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    }
})

// function to connect to the database 
async function connect_to_database(){
    try{
        await client.connect();
        await client.db('admin').command({ping: 1});
        console.log('pinged deployment. Successfully connected to the database');
    }
    catch(e){
        console.log(e)
    }
}

connect_to_database()

app.listen(process.env.PORT, (req, res)=>{
    console.log(`listening on port ${process.env.PORT}`)
    console.log(process.env.MONGODB_URI)
})

