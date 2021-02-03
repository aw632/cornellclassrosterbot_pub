import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio

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

def embed_builder(dep, num, url):
    em = requests.get(url)
    content = em.content
    dep_upper = dep.upper()

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
    elif ('PE' in full_class_name):
        distr_req = 'This class is a PE class and therefore satisfies one PE requirement.'
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
        prereq = prereq_prior.get_text().replace('Prerequisites/Corequisites', '').strip().replace('.', '')

    embed=discord.Embed(title=dep.upper() + ' ' + num + ': ' + full_class_name, url=url, description=full_class_descr, color=0xb31b1b)
    embed.add_field(name='Credits', value=credit_num, inline=True)
    embed.add_field(name='Distribution Requirements', value=distr_req, inline=True)
    embed.add_field(name='Semesters Offered', value=when_offered, inline=True)

    embed.add_field(name='Prerequisites/Corequisites', value=prereq, inline=True)
    embed.add_field(name='Reddit Search', value='[Click here](https://www.reddit.com/r/Cornell/search?q=' + dep_upper + '+' + num + '&restrict_sr=on&sort=relevance&t=all)', inline=True)
    embed.add_field(name='CUReviews', value='[Click here](https://www.cureviews.org/course/' + dep_upper + '/' + num + ')', inline=True)

    if (dep == 'CS'):
        cs_wiki_url = f'https://cornellcswiki.gitlab.io/classes/{dep}{num}.html'
        q = requests.get(cs_wiki_url)

        if (q.status_code == 404):
            embed.add_field(name="It seems like you're looking up a CS class!", value="However, it seems that this class does not have a CS wiki page :(", inline=True)
        else:
            embed.add_field(name="It seems like you're looking up a CS class!", value="[Click me to view the CS Wiki page for this class](https://cornellcswiki.gitlab.io/classes/" + dep + num + ".html)", inline=True)

    embed.set_footer(text='Questions, suggestions, problems? Write to mihari#4238')

    return embed

# fetch response code
async def fetch(session, url):
    async with session.get(url) as response:
        return response.status

# fetch response code from a bunch of urls
async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# dep = department, num = class number
# i.e. for the class MATH 2940, dep = MATH and num = 2940.
# dep can be upper or lower case. a space is required.
@client.command()
async def get(ctx, dep, num, sem = None):
    # easter 'egg'
    if (dep == 'PEN' and num == '15'):
        embed=discord.Embed(title="PEN15: [Redacted]", description="Introduction to the methods of CBT and high-level overview of fundamental Hornell concepts. Students will gain significant hands-on experience in the subject matter. Weekly pp sets will be assigned to reinforce understanding of the material. Note from the Instructor (Daddy): the course is well known for being extremely long and hard - many students do not feel they can meet the strenuous nightly demands of the course. It is not an easy ride. However it is mandatory for all Hornell majors so good luck.")
        embed.add_field(name='Credits', value="69", inline=True)
        embed.add_field(name='Distribution Requirements', value="May satisfy any request ;)", inline=True)
        embed.add_field(name='Semesters Offered', value="Every night at your mums house", inline=True)

        embed.add_field(name='Prerequisites/Corequisites', value="Good handle on human anatomical parts.", inline=True)
        embed.add_field(name='Reddit Search', value='[Click here](https://www.reddit.com/r/Cornell/search?q=PEN+15&restrict_sr=on&sort=relevance&t=all)', inline=True)
        embed.add_field(name='CUReviews', value='No reviews for this course. Those who take it are too banged up to write reviews.', inline=True)
        await ctx.send(embed=embed)

    elif (dep == 'PE' and num == '1173'):
        embed=discord.Embed(title="PE 1173: Lap Dance", description="Lap Dance, as it is called in the West, is an exciting and erotic dance or striptease performed close to, or sitting on the lap of, a paying customer. Learning the correct posture and basic movements that are used in the many styles of this dance, we will combine movements and isolations of the body and put them together into several different dances, including practice on a man with a wife and kids. Dancing to the variety of “bow chicka wow wow” songs is a fun, relaxing, stress free way to enjoy the day while developing flexibility, body awareness and overall body tone. Very little clothing is worn and the instructor provides lingerie to use in class, if you have a whip please feel free to wear it in class.")
        embed.add_field(name='Credits', value="", inline=True)
        embed.add_field(name='Distribution Requirements', value="", inline=True)
        embed.add_field(name='Semesters Offered', value="", inline=True)

        embed.add_field(name='Prerequisites/Corequisites', value="Good handle on human anatomical parts.", inline=True)
        embed.add_field(name='Reddit Search', value='[Click here](https://www.reddit.com/r/Cornell/search?q=PE+1173&restrict_sr=on&sort=relevance&t=all)', inline=True)
        embed.add_field(name='CUReviews', value='', inline=True)
        await ctx.send(embed=embed)

    else:
        url = ''
        if not sem: # if nothing is passed in for semester arg
            url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep.upper()}/{num}'
        else:
            url = 'https://classes.cornell.edu/browse/roster/' + sem + '/class/' + f'{dep.upper()}/{num}'
        # url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep.upper()}/{num}'
        dep_upper = dep.upper()
        r = requests.get(url)

        if (r.status_code == 410):
            sem_urls = [
                'https://classes.cornell.edu/browse/roster/SP20/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA20/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP19/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA19/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP18/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA18/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP17/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA17/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP16/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA16/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP15/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA15/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/SP14/class/' + f'{dep_upper}/{num}',
                'https://classes.cornell.edu/browse/roster/FA14/class/' + f'{dep_upper}/{num}',

            ]
            # sem_list = ['SP20', 'FA20', 'SP19', 'FA19', 'SP18', 'FA18', 'SP17', 'FA17', 'SP16', 'FA16', 'SP15', 'FA15', 'SP14', 'FA14'] # everything up to but not including the current semester

            # add one line

            # for x in sem_list:
            #     temp_url = 'https://classes.cornell.edu/browse/roster/' + x + '/class/' + f'{dep.upper()}/{num}'
            #     y = requests.head(temp_url)
            #     if (y.status_code == 200):
            #         await ctx.send(embed=embed_builder(dep, num, temp_url))
            #         break
            async with aiohttp.ClientSession() as session:
                res_codes = await fetch_all(session, sem_urls)
            if 200 in res_codes:
                succ_index = res_codes.index(200)
                await ctx.send(embed=embed_builder(dep, num, sem_urls[succ_index]))
            else:
                embed=discord.Embed(title="410: Class not found~", description="We searched all the way back to 2014, but still couldn't locate the class you asked us to find. It doesn't seem to be a real class, or it may no longer be offered at Cornell. You might also want to check the spelling of your command.", color=0xb31b1b)
                embed.set_footer(text="Questions, suggestions, problems? Write to mihari#4238")
                await ctx.send(embed=embed)

        elif (r.status_code == 404):
            embed=discord.Embed(title="404: Not found~", description="We couldn't locate the requested semester in student center! Remember that semesters are formatted as XXYY, where XX: SP = Spring, FA = Fall, WI = Winter, and SU = Summer, and where YY: the two digit year.", color=0xb31b1b)
            embed.set_footer(text="Questions, suggestions, problems? Write to mihari#4238")
            await ctx.send(embed=embed)

        else:
            await ctx.send(embed=embed_builder(dep, num, url))

client.run('ODAwMDE5NTYxMjM5Njc0ODkw.YAMCRw.FGX2G3WaA85uxAMZcU-Qi1g5mr8')
