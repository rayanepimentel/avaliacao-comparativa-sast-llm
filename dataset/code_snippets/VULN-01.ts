filterTable () {
   let queryParam: string = this.route.snapshot.queryParams.q
   if (queryParam) {
     queryParam = queryParam.trim()
     this.ngZone.runOutsideAngular(() => { 
       this.io.socket().emit('verifyLocalXssChallenge', queryParam)
     }) 
     this.dataSource.filter = queryParam.toLowerCase()
     this.searchValue = this.sanitizer.bypassSecurityTrustHtml(queryParam) 
     this.gridDataSource.subscribe((result: any) => {
       if (result.length === 0) {
         this.emptyState = true
       } else {
         this.emptyState = false
       }
     })
   } else {
     this.dataSource.filter = ''
     this.searchValue = undefined
     this.emptyState = false
   }
 }
