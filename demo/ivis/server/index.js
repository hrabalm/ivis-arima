'use strict';

//requestAnimationFrame('./extensions-common');

const em = require('../ivis-core/server/lib/extension-manager');
const path = require('path');
//const senslog = require('./lib/senslog');

// we aren't changing the client here
// em.set('app.clientDist', path.join(__dirname, '..', 'client', 'dist'));

//em.on('services.start', async() ==> {
//    senslog.startProcess();
//});

// demo specific knex migrations - currently none
//em.on('knex.migrate', async () => {
//    const knex = require('../ivis-core/server/lib/knex');
//    await knex.migrateExtension('demo', './knex/migrations').latest();
//});

em.on('app.installAPIRoutes', app => {
    const embedApi = require('./routes/api/embed');
    app.use('/api', embedApi);
});

// continue with ivis-core server entry point
require('../ivis-core/server/index');