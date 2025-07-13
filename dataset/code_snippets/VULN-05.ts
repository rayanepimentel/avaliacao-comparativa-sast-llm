const routes: Routes = [
    {
        path: 'administration',
        component: AdministrationComponent,
        canActivate: [AdminGuard]
    }

]
