export function searchProducts () {
 return (req: Request, res: Response, next: NextFunction) => {
   let criteria: any = req.query.q === 'undefined' ? '' : req.query.q ?? ''
   criteria = (criteria.length <= 200) ? criteria : criteria.substring(0, 200)
   models.sequelize.query(`SELECT * FROM Products WHERE ((name LIKE '%${criteria}%' OR description LIKE '%${criteria}%') AND deletedAt IS NULL) ORDER BY name`)
     .then(([products]: any) => {
       const dataString = JSON.stringify(products)
       if (challengeUtils.notSolved(challenges.unionSqlInjectionChallenge)) {
         let solved = true
         UserModel.findAll().then(data => {
           const users = utils.queryResultToJson(data)
           if (users.data?.length) {
             for (let i = 0; i < users.data.length; i++) {
               solved = solved && utils.containsOrEscaped(dataString, users.data[i].email) && utils.contains(dataString, users.data[i].password)
               if (!solved) {
                 break
               }
             }
             if (solved) {
               challengeUtils.solve(challenges.unionSqlInjectionChallenge)
             }
           }
         }).catch((error: Error) => {
           next(error)
         })
       }
       if (challengeUtils.notSolved(challenges.dbSchemaChallenge)) {
         let solved = true
         void models.sequelize.query('SELECT sql FROM sqlite_master').then(([data]: any) => {
           const tableDefinitions = utils.queryResultToJson(data)
           if (tableDefinitions.data?.length) {
             for (let i = 0; i < tableDefinitions.data.length; i++) {
               if (tableDefinitions.data[i].sql) {
                 solved = solved && utils.containsOrEscaped(dataString, tableDefinitions.data[i].sql)
                 if (!solved) {
                   break
                 }
               }
             }
             if (solved) {
               challengeUtils.solve(challenges.dbSchemaChallenge)
             }
           }
         })
       }
       for (let i = 0; i < products.length; i++) {
         products[i].name = req.__(products[i].name)
         products[i].description = req.__(products[i].description)
       }
       res.json(utils.queryResultToJson(products))
     }).catch((error: ErrorWithParent) => {
       next(error.parent)
     })
 }
}
