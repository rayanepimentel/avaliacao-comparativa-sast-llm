export function updateProductReviews () {
 return (req: Request, res: Response, next: NextFunction) => {
   const user = security.authenticatedUsers.from(req) 
   db.reviewsCollection.update( 
     { _id: req.body.id }, 
     { $set: { message: req.body.message } },
     { multi: true } 
   ).then(
     (result: { modified: number, original: Array<{ author: any }> }) => {
       challengeUtils.solveIf(challenges.noSqlReviewsChallenge, () => { return result.modified > 1 }) 
       challengeUtils.solveIf(challenges.forgedReviewChallenge, () => { return user?.data && result.original[0] && result.original[0].author !== user.data.email && result.modified === 1 })
       res.json(result)
     }, (err: unknown) => {
       res.status(500).json(err)
     })
 }
}
