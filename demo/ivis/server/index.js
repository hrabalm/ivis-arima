'use strict';

const em = require('../ivis-core/server/lib/extension-manager');
const path = require('path');

em.on('app.installAPIRoutes', app => {
    const embedApi = require('./routes/api/embed');
    app.use('/api', embedApi);
});

// continue with ivis-core server entry point
require('../ivis-core/server/index');