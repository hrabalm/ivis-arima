'use strict';

const em = require('../ivis-core/server/lib/extension-manager');
const path = require('path');

em.on('app.installAPIRoutes', app => {
    const api = require('./routes/api/api');
    app.use('/api', api);
});

// continue with ivis-core server entry point
require('../ivis-core/server/index');