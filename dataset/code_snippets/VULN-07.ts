
 return async (req: Request, res: Response, next: NextFunction) => {
   if (req.body.imageUrl !== undefined) {
     const url = req.body.imageUrl
     if (url.match(/(.)*solve\/challenges\/server-side(.)*/) !== null) req.app.locals.abused_ssrf_bug = true
     const loggedInUser = security.authenticatedUsers.get(req.cookies.token)
     if (loggedInUser) {
       try {...}