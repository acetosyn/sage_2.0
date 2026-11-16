"""Editable starter ideas, not market quotations or preloaded sales."""
# Every registration type has its own vocabulary and starter offerings.
PROFILES = {
'retail_shop': ('My shop', 'Products & prices', 'Shop sales', ['Rice (1 kg)', 'Cooking oil (1 litre)', 'Detergent']),
'wholesale_trading': ('My trade desk', 'Wholesale price list', 'Bulk orders', ['Carton supply', 'Bag supply', 'Delivery service']),
'ecommerce': ('My online store', 'Online listings', 'Online orders', ['Featured product', 'Gift bundle', 'Delivery fee']),
'pos_agent_banking': ('My agent desk', 'Service charges', 'Commission earned', ['Withdrawal charge', 'Transfer charge', 'Bill payment commission']),
'pastries_bakery': ('My bakery', 'Cakes & treats', 'Bakery sales', ['Meat pie', 'Birthday cake', 'Puff-puff pack', 'Chin chin']),
'chef_catering': ('My food business', 'Food menu & prices', 'Meals sold', ['Jollof rice & chicken', 'Fried rice', 'Egusi & swallow', 'Moi moi', 'Catering plate']),
'restaurant_food': ('My food business', 'Food menu & prices', 'Meals sold', ['Jollof rice', 'Fried rice', 'Amala & ewedu', 'Egusi & pounded yam', 'Beans & plantain', 'Suya', 'Small chops', 'Zobo']),
'photography': ('My photo studio', 'Photo packages', 'Shoots & earnings', ['Portrait session', 'Birthday shoot', 'Event coverage']),
'videography_content': ('My creator studio', 'Video packages', 'Projects & earnings', ['Reel production', 'Event film', 'Video editing']),
'digital_marketing': ('My marketing desk', 'Marketing packages', 'Client revenue', ['Social media management', 'Ad campaign setup', 'Content calendar']),
'graphic_design': ('My design studio', 'Design price list', 'Design earnings', ['Logo design', 'Flyer design', 'Brand identity']),
'fashion': ('My fashion studio', 'Styles & prices', 'Outfit orders', ['Ankara outfit', 'Agbada', 'Alteration', 'Ready-to-wear']),
'beauty': ('My beauty studio', 'Salon services', 'Beauty earnings', ['Braids', 'Nail set', 'Wig installation']),
'barber': ('My barber shop', 'Cuts & prices', 'Haircuts today', ['Adult haircut', 'Kids haircut', 'Beard trim']),
'makeup': ('My makeup studio', 'Makeup services', 'Client sessions', ['Soft glam', 'Full glam', 'Bridal makeup', 'Gele tying', 'Makeup lesson']),
'event_planning': ('My events studio', 'Event packages', 'Event earnings', ['Birthday decoration', 'Wedding coordination', 'Chair rental']),
'model_talent': ('My talent desk', 'Booking rates', 'Talent earnings', ['Brand shoot', 'Runway appearance', 'Event appearance']),
'transport': ('My ride business', 'Routes & fares', 'Trip earnings', ['Local trip', 'Airport transfer', 'Daily hire']),
'dispatch_courier': ('My delivery desk', 'Delivery rates', 'Delivery earnings', ['Local delivery', 'Express delivery', 'Bulk dispatch']),
'construction_artisan': ('My workshop', 'Jobs & quotes', 'Job earnings', ['Installation', 'Repair visit', 'Maintenance']),
'agriculture': ('My farm business', 'Produce & prices', 'Farm sales', ['Vegetable basket', 'Maize bag', 'Plantain bunch']),
'poultry_livestock': ('My livestock business', 'Stock & prices', 'Farm sales', ['Egg crate', 'Broiler', 'Catfish (kg)']),
'health_wellness': ('My wellness practice', 'Service list', 'Service earnings', ['Wellness session', 'Group workshop', 'Follow-up session']),
'fitness': ('My fitness studio', 'Training packages', 'Training earnings', ['Personal training', 'Monthly coaching', 'Group class']),
'real_estate_agent': ('My property desk', 'Agent services', 'Commission earned', ['Letting commission', 'Sales commission', 'Property management fee']),
'consulting': ('My consulting desk', 'Consulting packages', 'Consulting earnings', ['Consultation', 'Project review', 'Monthly retainer']),
 'training_tutoring': ('My tutoring business', 'Lessons & fees', 'Lesson earnings', ['Private lesson', 'Exam preparation', 'Weekend class']),
'technology': ('My tech studio', 'Tech services', 'Project earnings', ['Business website', 'App development', 'IT support']),
'freelance': ('My freelance desk', 'Service packages', 'Freelance earnings', ['Starter project', 'Hourly work', 'Monthly retainer']),
'influencer': ('My creator business', 'Rate card', 'Creator revenue', ['Sponsored reel', 'Brand ambassadorship', 'Affiliate commission', 'Platform payout', 'Story mention']),
'laundry': ('My laundry business', 'Laundry price list', 'Laundry earnings', ['Shirt wash & iron', 'Duvet cleaning', 'Suit dry cleaning']),
'phone_repairs': ('My repair desk', 'Repair services', 'Repair earnings', ['Screen replacement', 'Battery replacement', 'Diagnostics']),
'cleaning': ('My cleaning business', 'Cleaning packages', 'Cleaning earnings', ['Home cleaning', 'Move-in cleaning', 'Office cleaning']),
'data_airtime': ('My recharge business', 'Data & airtime plans', 'Commission earned', ['Data sale commission', 'Airtime commission', 'Utility commission']),
'perfume': ('My fragrance shop', 'Fragrances & prices', 'Fragrance sales', ['Perfume oil (10 ml)', 'Body mist', 'Gift set']),
'other': ('My business', 'Products & services', 'Sales & earnings', ['My first product', 'My first service'])}

FEATURES = {
'offerings': ('Products & services', 'Set your own selling prices and estimated unit costs.', 'catalog'),
'sales': ('Sales & earnings', 'Record money received. Select an offering to track quantities.', 'income'),
'costs': ('Business spending', 'Record actual costs once, including ingredients, transport, data and rent.', 'expenses'),
'savings': ('Savings pots', 'Daily, weekly or monthly goals. Record money you have actually set aside.', 'wallet'),
'bookings': ('Bookings & jobs', 'Keep client appointments, delivery dates and work in progress together.', 'calendar'),
'clients': ('My customers', 'Remember contact details, preferences and follow-up dates.', 'users'),
'stock': ('Stock & supplies', 'Track supplies, restocks, usage and low-stock levels.', 'inventory'),
'goals': ('Growth targets', 'Set a dated money target and update your progress.', 'analytics'),
 'tasks': ('My to-do list', 'Plan your next step and mark work complete.', 'check'),
'debts': ('Money owed to me', 'Track outstanding customer balances and repayments.', 'wallet'),
'plans': ('Startup budget', 'Compare planned purchases against what you actually spend.', 'briefcase'),
'campaigns': ('Promotions & brand deals', 'Track partners, deliverables, reach and campaign fees.', 'sparkles'),
'pricing': ('Price calculator', 'Estimate a sustainable price using cost and your target gross margin.', 'analytics'),
'reports': ('My business report', 'Review daily, weekly and monthly results; export your records.', 'reports'),
'drawings': ('My personal withdrawals', 'Separate money taken home from business operating costs.', 'wallet'),
'capital': ('Money I put in', 'Track owner funding separately from sales revenue.', 'income'),
'recurring': ('Bills & renewals', 'Plan due dates for rent, data, utilities and subscriptions.', 'calendar'),
'profile': ('My business setup', 'Change your business category as your work grows.', 'settings')}

def profile_for(user):
    key = getattr(user.organization.workspace_profile, 'business_category_key', 'other')
    home, offering, sales, suggestions = PROFILES.get(key, PROFILES['other'])
    return dict(key=key, home=home, offering=offering, sales=sales, suggestions=suggestions)

def solo_navigation(user):
    p=profile_for(user)
    groups=[('MY BUSINESS', [('dashboard',p['home'],'dashboard'),('solo_offerings',p['offering'],'catalog'),('solo_sales',p['sales'],'income'),('solo_costs','Business spending','expenses'),('solo_bookings','Bookings & jobs','calendar')]),
            ('MY MONEY', [('solo_reports','Profit & progress','analytics'),('solo_savings','Savings pots','wallet'),('solo_debts','Money owed to me','wallet'),('solo_drawings','Money I take home','wallet'),('solo_capital','Money I put in','income')]),
            ('BUILD & GROW', [('solo_'+k,FEATURES[k][0],FEATURES[k][2]) for k in ['clients','stock','pricing','goals','tasks','plans','campaigns','recurring']]),
            ('MY WORKSPACE', [('solo_profile','My business setup','settings'),('staff','My helpers','users'),('events','My events & workshops','calendar'),('settings','Preferences','settings')])]
    return [dict(section=name,key='solo-'+str(i),tone=['blue','violet','orange','blue'][i],items=[dict(page=page,label=label,icon={'catalog':'cart','income':'receipt','expenses':'wallet','calendar':'clock'}.get(icon,icon)) for page,label,icon in items]) for i,(name,items) in enumerate(groups)]
