

const user = security.authenticatedUsers.from(req)
if (user && basketIds[0] && basketIds[0] !== 'undefined' && Number(user.bid) != Number(basketIds[0])) {
    res.status(401).send('{\'error\' : \'Invalid BasketId\'}')
} else {
    const basketItem = {
        ProductId: productIds[productIds.length - 1],
        BasketId: basketIds[basketIds.length - 1],
        quantity: quantities[quantities.length - 1]
    }
    challengeUtils.solveIf(challenges.basketManipulateChallenge, () => { return user && basketItem.BasketId && basketItem.BasketId !== 'undefined' && user.bid != basketItem.BasketId })


    const basketItemInstance = BasketItemModel.build(basketItem)
    basketItemInstance.save().then((addedBasketItem: BasketItemModel) => {
        res.json({ status: 'success', data: addedBasketItem })
    }).catch((error: Error) => {
        next(error)
    })
}