import discord
import lxml
from discord.ext import commands
import requests
import re
from bs4 import BeautifulSoup
import aiohttp
import rmp_class
import asyncio
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
import json
import pickle
from fastDamerauLevenshtein import damerauLevenshtein
import os


cornell_red = 0xB31B1B

intents = discord.Intents(
    messages=True, guilds=True, reactions=True, members=True, presences=True
)

client = commands.Bot(command_prefix="c!", intents=intents)
slash = SlashCommand(client, sync_commands=True)


@client.command()
@commands.is_owner()
async def servers(ctx):
    servers = list(client.guilds)
    await ctx.send(f"Connected on {str(len(servers))} servers:")
    await ctx.send("\n".join(guild.name for guild in servers))


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.dnd, activity=discord.Game("in Okenshields")
    )
    print("Bot is ready.")


@client.command()
@commands.is_owner()
async def logout(ctx):
    await ctx.send("Shutting down! I'm audi")
    await client.close()


@client.command()
@commands.is_owner()
async def timer(ctx, first, second):
    first_shifted = (int(first) >> 22) + 1420070400000
    second_shifted = (int(second) >> 22) + 1420070400000
    length = (second_shifted - first_shifted) / 1000
    await ctx.send(f"Time between first and second was {str(length)} seconds.")


def listToString(s):
    str1 = ", "
    return str1.join(s)


def get_most_matching(target, threshold, namesList):
    matchers = []
    for name in namesList:
        result = damerauLevenshtein(target, name, similarity=True)
        if result >= threshold:
            matchers.append(name)

    return matchers


def get_descriptions(soup):
    """Returns the Full Class Name and Full Class Description from a site.

    Args:
        soup (BeautifulSoup Object): represents the webpage in bs4
    """
    full_class_name = soup.find(class_="title-coursedescr").get_text()

    full_class_descr = soup.find(class_="catalog-descr").get_text().strip()

    return full_class_name, full_class_descr


def safe_get_data(soup, html_class, error_message):
    """Safely (i.e. can recognize NoneType) retrieves relevant data.
    Note: works with span only

    Args:
        soup (BeautifulSoup Object): represents the webpage in bs4
        html_class (string): the htmlt id of the relevant data in soup object
        error_mesasge (string): the specified error message if NoneType object is found.
    """
    try:
        result = soup.find("span", {"class": html_class}).get_text().strip()
    except AttributeError:
        result = error_message

    return result


def get_cswiki(num):
    """If the class is a CS class, attempt to find the relevant CS wiki page.
    Return relevant strings for embed builder.

    Args:
        num (string): class number
    """
    cs_wiki_url = f"https://cornellcswiki.gitlab.io/classes/CS{num}.html"
    q = requests.head(cs_wiki_url)

    name = "It seems like you're looking up a CS class!"

    if q.status_code == 404:
        value = "However, it seems that this class does not have a CS wiki page :("
    else:
        value = (
            "[Click me to view the CS Wiki page for this class](https://cornellcswiki.gitlab.io/classes/CS"
            + num
            + ".html)"
        )

    return name, value


def safe_get_prof(soup, error_message):
    """Safely (i.e. can handle NoneType) gets prof name from webpage represented as a
    soup object. Because the web scraping protocol is slightly modifed, we don't
    include it in the other helper method.

    Args:
        soup (string): BeautifulSoup representation of a webpage.
        error_message (string): What to return if we encounter NoneType.
    """
    parsed_prof_name_lst = []
    i_result = soup.find("li", {"class": "instructors"}).select("p > span")
    if i_result != []:
        result = [x["data-content"] for x in i_result]
        parsed_prof_name_lst = [re.sub("\(.*\)", "", res).strip() for res in result]
    else:
        parsed_prof_name_lst.append(error_message)
    return parsed_prof_name_lst


def make_rmp_list(prof_list):
    """Returns a list of tuples of form (profname1, rating1, url1).

    Args:
        prof_list (string list): List of professor names for a class.
    """
    pfd = json.load(open("profDictionary.json"))

    rating_lst = []
    url_lst = []
    for parsed_prof_name in prof_list:
        if parsed_prof_name in pfd:
            dictValue = pfd[parsed_prof_name]
            rating_lst.append(dictValue[0])
            url_lst.append(dictValue[1])
        else:
            rmp_url = rmp_class.get_prof_url(parsed_prof_name)

            if rmp_url == 404:
                final_url = "N/A"
                rating = "N/A"
            else:
                final_url = rmp_url
                rating = rmp_class.get_rating(rmp_url)

            url_lst.append(final_url)
            rating_lst.append(rating)

            pfd[parsed_prof_name] = (rating, final_url)

    j = json.dumps(pfd)
    with open("profDictionary.json", "w") as f:
        f.write(j)
        f.close()

    result_list = list(zip(prof_list, rating_lst, url_lst))
    return result_list


def value_string_builder(lst):
    """Builds a string formatted in such way: [prof name, rating](url)

    Args:
        lst (list): list of tuples (prof name, rating, url)
    """
    result = ""
    # print(lst)
    for tup in lst:
        if tup[2] == "N/A":
            result = result + "{}, {}\n".format(tup[0], tup[1])
        else:
            result = result + "[{}, {}]({})\n".format(tup[0], tup[1], tup[2])
    return result


def embed_builder(dep, num, url):
    semester = re.search("([SF][A-Z]*[0-9]+)", url).group(1)
    em = requests.get(url)
    content = em.content
    dep_upper = dep.upper()

    soup = BeautifulSoup(content, "lxml")

    full_class_name, full_class_descr = get_descriptions(soup)

    parsed_prof_name_lst = safe_get_prof(soup, "Staff")

    result_list = make_rmp_list(parsed_prof_name_lst)

    credit_num = safe_get_data(
        soup, "credit-val", "For some reason, the number of credits is not listed."
    )

    distr_req_prior = safe_get_data(
        soup,
        "catalog-distr",
        "N/A: This class does not satisfy any distribution requirements.",
    )

    if "FWS" in full_class_name:
        distr_req = "This class is a First-year Writing Seminar and therefore satisfies one FWS requirement."
    elif "PE" in full_class_name:
        distr_req = (
            "This class is a PE class and therefore satisfies one PE requirement."
        )
    else:
        distr_req = distr_req_prior.replace("Distribution Category", "")

    when_offered = safe_get_data(
        soup,
        "catalog-when-offered",
        "N/A: For some reason, we don't know when this class is usually offered.",
    ).replace("When Offered", "")

    prereq = safe_get_data(
        soup,
        "catalog-prereq",
        "N/A: This class does not have any prerequisites, or none are listed.",
    ).replace("Prerequisites/Corequisites", "")

    embed = discord.Embed(
        title=dep.upper() + " " + num + ": " + full_class_name,
        url=url,
        description=full_class_descr,
        color=cornell_red,
    )
    embed.add_field(name="Credits", value=credit_num, inline=True)
    embed.add_field(name="Distribution Requirements", value=distr_req, inline=True)
    embed.add_field(name="Semesters Offered", value=when_offered, inline=True)

    embed.add_field(name="Prerequisites/Corequisites", value=prereq, inline=True)
    embed.add_field(
        name="Reddit Search",
        value="[Click here](https://www.reddit.com/r/Cornell/search?q="
        + dep_upper
        + "+"
        + num
        + "&restrict_sr=on&sort=relevance&t=all)",
        inline=True,
    )
    embed.add_field(
        name="CUReviews",
        value="[Click here](https://www.cureviews.org/course/"
        + dep_upper
        + "/"
        + num
        + ")",
        inline=True,
    )

    prof_bunch = value_string_builder(result_list)
    # print(prof_bunch)
    embed.add_field(name="Professor(s)", value=prof_bunch, inline=True)
    # embed.add_field(name="RateMyProfessor Link", value="Placeholder", inline=True)
    # TODO: put last offered somewhere else, and instead include median grade.
    embed.add_field(name="Latest Offering", value=semester, inline=True)

    if dep_upper == "CS":
        n, v = get_cswiki(num)
        embed.add_field(
            name=n,
            value=v,
            inline=True,
        )

    embed.set_footer(text="Questions, suggestions, problems? Write to mihari#4238")

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


@slash.slash(
    name="get",
    description="gets information about a class",
    options=[
        manage_commands.create_option(
            name="dep",
            description="the subject acronym, e.g. 'CS' for Computer Science",
            option_type=3,
            required=True,
        ),
        manage_commands.create_option(
            name="num", description="4 digit class number", option_type=3, required=True
        ),
    ],
    guild_ids=None,
)

# dep = department, num = class number
# i.e. for the class MATH 2940, dep = MATH and num = 2940.
# dep can be upper or lower case. a space is required.
@client.command()
async def get(ctx, dep, num):

    if (dep.upper() == "MIHARI") and (num == "1110"):
        await ctx.send(
            "If you are reading this, it means that Easter Egg worked finally."
        )
    elif (dep.upper() == "ANTHR") and (num == "3552"):
        await ctx.send(
            "The class is blocked from classrosterbot. Please view it at classes.cornell.edu if you want it."
        )
    else:
        url = (
            "https://classes.cornell.edu/browse/roster/FA21/class/"
            + f"{dep.upper()}/{num}"
        )
        # url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep.upper()}/{num}'
        dep_upper = dep.upper()
        r = requests.get(url)

        merged_string = f"{dep_upper} {num}"

        if r.status_code == 410:
            sem_urls = [
                "https://classes.cornell.edu/browse/roster/SP21/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP20/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA20/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP19/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA19/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP18/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA18/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP17/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA17/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP16/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA16/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP15/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA15/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/SP14/class/"
                + f"{dep_upper}/{num}",
                "https://classes.cornell.edu/browse/roster/FA14/class/"
                + f"{dep_upper}/{num}",
            ]

            async with aiohttp.ClientSession() as session:
                res_codes = await fetch_all(session, sem_urls)
            if 200 in res_codes:
                succ_index = res_codes.index(200)
                await ctx.send(embed=embed_builder(dep, num, sem_urls[succ_index]))
            else:
                # with open("classnames.bin", "rb") as fp:
                #     x = pickle.load(fp)

                # typos = listToString(get_most_matching(merged_string, 0.7, x))
                embed = discord.Embed(
                    title="410: Class not found~",
                    description="We searched all the way back to 2014, but still couldn't locate the class you asked us to find. It doesn't seem to be a real class, or it may no longer be offered at Cornell. You might also want to check the spelling of your command.",
                    color=cornell_red,
                )
                # if len(typos) > 0:
                #     embed.add_field(
                #         name="Perhaps you meant:",
                #         value=typos,
                #         inline=True,
                #     )

                embed.set_footer(
                    text="Questions, suggestions, problems? Write to mihari#4238"
                )
                await ctx.send(embed=embed)

        elif r.status_code == 404:
            embed = discord.Embed(
                title="404: Not found~",
                description="We couldn't locate the requested semester in student center! Remember that semesters are formatted as XXYY, where XX: SP = Spring, FA = Fall, WI = Winter, and SU = Summer, and where YY: the two digit year.",
                color=cornell_red,
            )
            embed.set_footer(
                text="Questions, suggestions, problems? Write to mihari#4238"
            )
            await ctx.send(embed=embed)

        else:
            # with open("classnames.bin", "rb") as fp:
            #     x = pickle.load(fp)

            # if merged_string not in x:
            #     x.add(merged_string)

            # with open("classnames.bin", "wb") as fp:
            #     pickle.dump(x, fp)

            await ctx.send(embed=embed_builder(dep, num, url))


debug = True
if not debug:
    token = os.environ.get("TOKEN")
else:
    # Create a file called token.txt, and only copy paste the token, don't put anything else, no quotes no empty spaces nothing.
    t = open("token.txt")
    lines = t.readlines()
    token = lines[0]

client.run(token)
