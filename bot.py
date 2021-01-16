import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)

client = commands.Bot(command_prefix = 'c!', intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game('in Okenshields'))
    print('Bot is ready.')

@client.command()
@commands.is_owner()
async def logout(ctx):
    await ctx.send('Shutting down! I\'m audi')
    await client.logout()

# dep = department, num = class number
# i.e. for the class MATH 2940, dep = MATH and num = 2940.
# dep can be upper or lower case. a space is required.
@client.command()
async def get(ctx, dep, num, sem = None):
    url = ''
    if not sem: # if nothing is passed in for semester arg
        url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep.upper()}/{num}'
    else:
        url = 'https://classes.cornell.edu/browse/roster/' + sem + '/class/' + f'{dep.upper()}/{num}'
    # url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep.upper()}/{num}'
    dep_upper = dep.upper()
    r = requests.get(url)

    if (r.status_code == 410):
        embed=discord.Embed(title="410: Class not found~", description="We couldn't locate the class you asked us to find. This is probably because it isn't offered this semester! You might also want to check the spelling of your command.", color=0xb31b1b)
        embed.set_footer(text="Questions, suggestions, problems? Write to mihari#4238")
        await ctx.send(embed=embed)

    elif (r.status_code == 404):
        embed=discord.Embed(title="404: Not found~", description="We couldn't locate the requested semester in student center! Remember that semesters are formatted as XXYY, where XX: SP = Spring, FA = Fall, WI = Winter, and SU = Summer, and where YY: the two digit year.", color=0xb31b1b)
        embed.set_footer(text="Questions, suggestions, problems? Write to mihari#4238")
        await ctx.send(embed=embed)

    else:
        content = r.content

        soup = BeautifulSoup(content, 'html.parser')

        full_class_name = soup.find(class_='title-coursedescr').get_text()

        full_class_descr = soup.find(class_='catalog-descr').get_text().strip()
        trun_class_descr = (full_class_descr[:168] + '..') if len(full_class_descr) > 168 else full_class_descr

        # spans = soup.find_all('span', {'class' : 'tooltip-iws'})
        # prof_name_netid = spans[6]['data-content'] <-- fix this? or leave it...

        credit_num = soup.find('span', {'class' : 'credit-val'}).get_text()

        distr_req_prior = soup.find('span', {'class' : 'catalog-distr'})

        if ('FWS' in full_class_name):
            distr_req = 'This class is a First-year Writing Seminar and therefore satisfies one FWS requirement.'
        elif (distr_req_prior is None):
            distr_req = 'N/A: This class does not satisfy any distribution requirements.'
        else:
            distr_req = distr_req_prior.get_text().replace('Distribution Category', '')

        when_offered_prior = soup.find('span', {'class' : 'catalog-when-offered'})

        if (when_offered_prior is None):
            when_offered = 'N/A: For some reason, we don\'t know when this class is usually offered.'
        else:
            when_offered = when_offered_prior.get_text().replace('When Offered', '').strip().replace('.', '')

        prereq_prior = soup.find('span', {'class' : 'catalog-prereq'})

        if (prereq_prior is None):
            prereq = 'N/A: This class does not have any prerequisites, or none are listed.'
        else:
            prereq = prereq_prior.get_text().replace(' Prerequisite', '').strip().replace('.', '')

        embed=discord.Embed(title=dep.upper() + ' ' + num + ': ' + full_class_name, url=url, description=full_class_descr, color=0xb31b1b)
        embed.add_field(name='Credits', value=credit_num, inline=True)
        embed.add_field(name='Distribution Requirements', value=distr_req, inline=True)
        embed.add_field(name='Semesters Offered', value=when_offered, inline=True)

        embed.add_field(name='Prerequisites', value=prereq, inline=True)
        embed.add_field(name='Reddit Search', value='[Click here](https://www.reddit.com/r/Cornell/search?q=' + dep_upper + '+' + num + '&restrict_sr=on&sort=relevance&t=all)', inline=True)
        embed.add_field(name='CUReviews', value='[Click here](https://www.cureviews.org/course/' + dep_upper + '/' + num + ')', inline=True)
        embed.set_footer(text='Questions, suggestions, problems? Write to mihari#4238')
        await ctx.send(embed=embed)

client.run('ODAwMDE5NTYxMjM5Njc0ODkw.YAMCRw.I_NFa3Yu3oFkZ1FsaH_3OKpxnnk')
