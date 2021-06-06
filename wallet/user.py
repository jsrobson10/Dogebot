
import glob

async def UserGet(guild, uid):

    try:
        return await guild.fetch_member(uid)
    except:
        return None

async def UserInServer(guild, uid):

    try:
        m = await guild.fetch_member(uid)
        return m is not None
    except:
        return False
