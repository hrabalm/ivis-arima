'use strict';

const passport = require('../../../ivis-core/server/lib/passport');
const router = require('../../../ivis-core/server/lib/router-async').create();
const signalSets = require('../../../ivis-core/server/models/signal-sets');
const signals = require('../../../ivis-core/server/models/signals');
const { castToInteger } = require('../../../ivis-core/server/lib/helpers');


router.getAsync('/predictions/:modelId', passport.loggedIn, async (req, res) => {
    return res.json();
});

router.postAsync('/signal-set/:signalSetCid', passport.loggedIn, async (req, res) => {
    return res.json();
});

router.postAsync('/signal-sets', passport.loggedIn, async (req, res) => {
    return res.json(await signalSets.create(req.context, req.body));
});

router.postAsync('/signals/:signalSetCid', passport.loggedIn, async (req, res) => {
    const set = await signalSets.getByCid(req.context, req.params.signalSetCid);
    console.log(await set.id);
    return res.json(await signals.create(req.context, set.id, req.body));
});

router.postAsync('/signal-set-records/:signalSetId', passport.loggedIn, async (req, res) => {
    const sigSetWithSigMap = await signalSets.getById(req.context, castToInteger(req.params.signalSetId), false, true);
    await signalSets.insertRecords(req.context, sigSetWithSigMap, [req.body]);
    return res.json();
});


router.getAsync('/signal-sets-by-cid/:signalSetCid', passport.loggedIn, async (req, res) => {
    const signalSet = await signalSets.getByCid(req.context, req.params.signalSetCid, true, false);
    signalSet.hash = signalSets.hash(signalSet);
    return res.json(signalSet);
});

module.exports = router;