from cProfile import label
from h2o_wave import main, app, Q, ui, data
import time
from faker import Faker
import random
from typing import List


_id = 0
class TodoItem:
    def __init__(self, label):
        global _id
        _id += 1
        self.id = f'todo_{_id}'
        self.done = False
        self.label = label
        
class FakeCategoricalSeries:
    def __init__(self, min=0.0, max=100.0, variation=10.0, start: int = None):
        self.series = FakeSeries(min, max, variation, start)
        self.i = 0

    def next(self):
        x, dx = self.series.next()
        self.i += 1
        return f'C{self.i}', x, dx


class FakeMultiCategoricalSeries:
    def __init__(self, min=0.0, max=100.0, variation=10.0, start: int = None, groups=5):
        self.series = [(f'G{c + 1}', FakeCategoricalSeries(min, max, variation, start)) for c in range(groups)]

    def next(self):
        data = []
        for g, series in self.series:
            c, x, dx = series.next()
            data.append((g, c, x, dx))
        return data

        
class FakeSeries:
    def __init__(self, min=0.0, max=100.0, variation=10.0, start: int = None):
        self.min = min
        self.max = max
        self.variation = variation
        self.start = random.randint(min, max) if start is None else start
        self.x = self.start

    def next(self):
        x0 = self.x
        x = x0 + (random.random() - 0.5) * self.variation
        if not self.min <= x <= self.max:
            x = self.start
        self.x = x
        dx = 0 if x0 == 0 else 100.0 * (x - x0) / x0
        return x, dx
         
class FakePercent:
    def __init__(self, min=5.0, max=35.0, variation=4.0):
        self.min = min
        self.max = max
        self.variation = variation
        self.x = random.randint(min, max)

    def next(self):
        self.x += random.random() * self.variation
        if self.x >= self.max:
            self.x = self.min
        return self.x, (self.x - self.min) / (self.max - self.min)

class FakeCategoricalSeries:
    def __init__(self, min=0.0, max=100.0, variation=10.0, start: int = None):
        self.series = FakeSeries(min, max, variation, start)
        self.i = 0

    def next(self):
        x, dx = self.series.next()
        self.i += 1
        return f'C{self.i}', x, dx

persona = 'https://scontent.fcmb1-2.fna.fbcdn.net/v/t1.6435-9/62108991_2085396404922307_4543300290715058176_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=730e14&_nc_ohc=aDY9hHZ2X08AX9Z1Ph6&_nc_ht=scontent.fcmb1-2.fna&oh=00_AT-ub5nHcQbSZao8Tqkz31zx9eSHMfWwsekqzMeQdVXGyQ&oe=62FFACE7'

n = 10
k = 5
f = FakeMultiCategoricalSeries(groups=k)
values = [(g, t, x) for x in [f.next() for _ in range(n)] for g, t, x, dx in x]

@app('/demo')
async def serve(q: Q):
    
    if q.args.new_todo:  
        await new_comment(q)
    elif q.args.add_todo:  
        await add_comment(q)
    else:  
        await show_comments(q)
    
    
    await Header_page(q)
    await Nav_page(q)
    await pie_chart(q)
    
    await card_Detail(q)
    
    await histogram(q)
    await Real_time_card(q)
    await chart_func(q)
    
    
    await q.page.save()

async def histogram(q:Q):
    v = q.page.add('example4', ui.plot_card(
        box='3 6 8 5',
        title='Intervals, stacked',
        data=data('country product price', n * k),
        plot=ui.plot([ui.mark(
            coord='rect',
            type='interval',
            x='=product',
            y='=price',
            y_min=0,
            color='=country',
            stack='auto',
        )]),
    ))
    v.data = values
    await q.page.save()


async def chart_func(q:Q):
    colors = '$red $pink '.split()
    curves = 'linear'.split()
    fake = Faker()
    cards = []
    for i in range(len(curves)):
        f = FakeCategoricalSeries()
        cat, val, pc = f.next()
        c = q.page.add(f'chart_{i}', ui.wide_series_stat_card(
            box=f'6 {i + 3} 5 3',
            title=fake.cryptocurrency_name(),
            value='=${{intl qux minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=val, quux=pc / 100),
            plot_category='foo',
            plot_type='area',
            plot_value='qux',
            plot_color=colors[i],
            plot_data=data('foo qux', -15),
            plot_zero_value=0,
            plot_curve=curves[i],
        ))
        cards.append((f, c))
    await q.page.save()
    
    while True:
        time.sleep(1)
        for f, c in cards:
            cat, val, pc = f.next()
            c.data.qux = val
            c.data.quux = pc / 100
            c.plot_data[-1] = [cat, val]
        await q.page.save()
    


async def pie_chart(q:Q):
    f = FakePercent()
    val1, _ = f.next()
    
    c = q.page.add('pie_chart', ui.wide_pie_stat_card(
    box='3 3 3 3',
    title='Account Detail',
    pies=[
        ui.pie(label='Withdraw ', value='35%', fraction=0.35, color='#2cd0f5', aux_value='$ 35'),
        ui.pie(label=' Deposit ', value='65%', fraction=0.65, color='$themePrimary', aux_value='$ 65'),
    ],
    ))
    
async def card_Detail(q:Q):
    q.page.add('cardDetails', ui.tall_stats_card(
    box='11 3 2 2',
    items=[
        ui.stat(label='ID 122 678 455', value=''),
        ui.stat(label='Your Income', value='$2,578'),
    ],
    ))    
  
async def new_comment(q: Q):
    # Display an input form
    q.page['form'] = ui.form_card(box='11 5 2 -1', items=[
        ui.text_l('New Transaction'),
        ui.textbox(name='label', label='Transfer Amount ?', multiline=True),
        ui.buttons([
            ui.button(name='add_todo', label='Pay', primary=True),
            ui.button(name='show_todos', label='Cancel'),
        ]),
    ])   

async def add_comment(q: Q):
    # Insert a new item
    q.user.todos.insert(0, TodoItem(q.args.label or 'Untitled'))

    # Go back to our list.
    await show_comments(q)

async def show_comments(q: Q):
    
    todos: List[TodoItem] = q.user.todos

    if todos is None:
        q.user.todos = todos = [TodoItem('Deposit Waste   $291'), TodoItem('Deposit Waste   $641'), TodoItem('Transfer Deposit   $80'), TodoItem('Deposit Lanka   $8000')]

    for todo in todos:
        if todo.id in q.args:
            todo.done = q.args[todo.id]
            
    done = [ui.checkbox(name=todo.id, label=todo.label, value=True, trigger=True) for todo in todos if todo.done]
    not_done = [ui.checkbox(name=todo.id, label=todo.label, trigger=True) for todo in todos if not todo.done]

    q.page['form'] = ui.form_card(box='11 5 2 -1', items=[
        ui.text_l('Last Transaction'),
        ui.button(name='new_todo', label='New Transaction...', primary=True),
        *not_done,
        *([ui.separator('Transaction Completed')] if len(done) else []),
        *done,
    ])
    await q.page.save()
    
      
async def Header_page(q: Q):
    q.page['header1'] = ui.header_card(
    box='1 1 -1 1',
    title='H2O Wave',
    subtitle='',
    image='https://wave.h2o.ai/img/h2o-logo.svg',

    secondary_items=[ui.textbox(name='search', icon='Search', width='300px', placeholder='Search...')],
    color='primary'
    )
    
    
     
async def Real_time_card(q:Q):
    fake = Faker()
    f = FakePercent()
    val, pc = f.next()
    val1, pc1 = f.next()
    val2, pc2 = f.next()
    
    c = q.page.add('progress1', ui.wide_gauge_stat_card(
        box='3 2 2 1',
        title=fake.cryptocurrency_name(),
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=pc,
        data=dict(foo=val, bar=pc),
        
    ))
    
    d = q.page.add('progress2', ui.wide_gauge_stat_card(
        box='5 2 2 1',
        title=fake.cryptocurrency_name(),
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=pc1,
        data=dict(foo=val1, bar=pc1),
        
    ))
     
    e = q.page.add('progress3', ui.wide_gauge_stat_card(
        box='7 2 2 1',
        title=fake.cryptocurrency_name(),
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=pc2,
        data=dict(foo=val2, bar=pc2),
        
    ))
    
    f = q.page.add('progress4', ui.wide_gauge_stat_card(
        box='9 2 4 1',
        title=fake.cryptocurrency_name(),
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=pc,
        data=dict(foo=val1, bar=pc),
        
    ))
    
 
 
    
async def Nav_page(q:Q):
    if '#' in q.args and not q.args.show_nav:
        hash_ = q.args['#']
        # q.page.drop()
        
        
        q.page['nav21'] = ui.nav_card(
            box='1 2 2 -1',
            value='#menu/ham',
            persona=ui.persona(title='Mahas Milhar', subtitle='Software Engineer', caption='Online', size='xl', image=persona),
            items=[
                
               
            ],
            secondary_items=[ui.button(name='show_nav', label='Back', width='100%')],
            color='primary'
        )
        
    else:
        q.page['meta'] = ui.meta_card(box='', redirect='#')
        q.page['nav1'] = ui.nav_card(
            box='1 2 2 -1',
            items=[
                ui.nav_group('Menu', items=[
                    ui.nav_item(name='#', label='Dashboard'),
                    ui.nav_item(name='#menu/profile', label='Profile'),
                    ui.nav_item(name='#menu/customer', label='Customer', disabled=True),
                    ui.nav_item(name='#menu/category', label='Category', disabled=True),
                    ui.nav_item(name='#menu/stock', label='Stock', disabled=True),
                    ui.nav_item(name='#menu/report', label='Report', disabled=True),
                ]),
                ui.nav_group('Help', items=[
                    ui.nav_item(name='#about', label='About', icon='Info'),
                    ui.nav_item(name='#support', label='Support', icon='Help'),
                ])
            ],
            color='primary'
        )
