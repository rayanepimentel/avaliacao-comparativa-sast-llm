const routes: Routes = [
  { 
    path: 'administration', 
    component: AdministrationComponent, 
    canActivate: [AdminGuard] 
  }, 
  {
    path: 'accounting',
    component: AccountingComponent,
    canActivate: [AccountingGuard]
  },
  {
    path: 'about',
    component: AboutComponent
  },
  {
    path: 'address/select',
    component: AddressSelectComponent,
    canActivate: [LoginGuard]
  },
  {
    path: 'address/saved',
    component: SavedAddressComponent,
    canActivate: [LoginGuard]
  },
  {
    path: 'address/create',
    component: AddressCreateComponent,
    canActivate: [LoginGuard]
  },
  {
    path: 'address/edit/:addressId',
    component: AddressCreateComponent,
    canActivate: [LoginGuard]
  },
  {
    path: 'delivery-method',
    component: DeliveryMethodComponent
  },
  {
    path: 'deluxe-membership',
    component: DeluxeUserComponent,
    canActivate: [LoginGuard]
  },
  {
    path: 'saved-payment-methods',
    component: SavedPaymentMethodsComponent
  },
  {
    path: 'basket',
    component: BasketComponent
  },
  {
    path: 'order-completion/:id',
    component: OrderCompletionComponent
  },
  {
    path: 'contact',
    component: ContactComponent
  },
  {
    path: 'photo-wall',
    component: PhotoWallComponent
  },
  {
    path: 'complain',
    component: ComplaintComponent
  },
  {
    path: 'chatbot',
    component: ChatbotComponent
  },
  {
    path: 'order-summary',
    component: OrderSummaryComponent
  },
  {
    path: 'order-history',
    component: OrderHistoryComponent
  },
  {
    path: 'payment/:entity',
    component: PaymentComponent
  },
  {
    path: 'wallet',
    component: WalletComponent
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },
  {
    path: 'recycle',
    component: RecycleComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  },
  {
    path: 'search',
    component: SearchResultComponent
  }
]