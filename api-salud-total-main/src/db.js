import pg from 'pg';
import { PG_USER, PG_DATABASE, PG_HOST, PG_PASSWORD, PG_PORT, PG_URL } from './config.js';

// Produccion
export const pool = new pg.Pool({
    host: PG_HOST,
    user: PG_USER,
    password: PG_PASSWORD,
    database: PG_DATABASE,
    port: PG_PORT,
    ssl: {
        rejectUnauthorized: false
    }
});