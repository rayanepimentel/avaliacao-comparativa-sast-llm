
 app.use('/ftp', serveIndexMiddleware, serveIndex('ftp', { icons: true })) 
 app.use('/ftp(?!/quarantine)/:file', servePublicFiles()) 
 app.use('/ftp/quarantine/:file', serveQuarantineFiles()) 


