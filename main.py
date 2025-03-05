import os
import discord
import requests  # ✅ ใช้ดึงข้อมูลจาก API
from discord.ext import commands
from discord import ui
from myserver import server_on

# ตั้งค่า Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ตั้งค่า KeyAuth API
KEYAUTH_SELLER_KEY = "87c3d5a7a8c98996b2cfb1669355406e"
KEYAUTH_API_URL = "https://keyauth.win/api/seller/"

# ใส่ Role ID และ Channel ID ที่ต้องการให้บอทใช้
CUSTOMER_ROLE_ID = 1279035218430263327  
CHANNEL_ID = 1279036071619072082  

# ✅ ฟังก์ชันตรวจสอบคีย์กับ KeyAuth API
def check_key_auth(key: str) -> bool:
    url = f"{KEYAUTH_API_URL}?sellerkey={KEYAUTH_SELLER_KEY}&type=validate&key={key}"
    response = requests.get(url)
    return response.text.strip() == "valid"

# เมื่อบอทออนไลน์ให้พิมพ์ข้อความใน Terminal และส่งข้อความไปที่ Discord
@bot.event
async def on_ready():
    print("✅ Bot is online and ready!")

    channel = bot.get_channel(CHANNEL_ID)  # ค้นหาแชนแนลที่กำหนด
    if channel and channel.permissions_for(channel.guild.me).send_messages:
        await channel.send("✅ Bot is now online and ready to use! Type `.send_redeem` to start.")
    else:
        print(f"❌ บอทไม่มีสิทธิ์ส่งข้อความ หรือไม่พบช่องแชท ID: {CHANNEL_ID}")

# คำสั่งให้บอทส่ง Embed พร้อมปุ่ม Claim Role
@bot.command()
async def send_redeem(ctx):
    embed = discord.Embed(title="REDEEM KEY",
                          description="👉 ใส่คีย์ของคุณเพื่อรับยศ",
                          color=discord.Color.blue())
    embed.set_footer(text="Developed by 11111")

    view = ClaimRoleView()
    await ctx.send(embed=embed, view=view)

# ปุ่ม Claim Role (ป้องกันหมดอายุ)
class ClaimRoleView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ✅ ทำให้ปุ่มอยู่ถาวร
        self.add_item(ClaimRoleButton())

class ClaimRoleButton(ui.Button):
    def __init__(self):
        super().__init__(label="🔑 Claim Role", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        modal = RedeemForm()
        await interaction.response.send_modal(modal)

# ฟอร์ม Modal สำหรับให้ผู้ใช้กรอกคีย์
class RedeemForm(ui.Modal, title="Claim Your License"):
    invoice_id = ui.TextInput(label="KEY", placeholder="ใส่คีย์", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        key = self.invoice_id.value.strip()  # รับค่าจากฟอร์มและตัดช่องว่าง
        role = interaction.guild.get_role(CUSTOMER_ROLE_ID)

        # ✅ ตรวจสอบคีย์กับ KeyAuth API
        if check_key_auth(key):
            if role:
                await user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ **Success!** {user.mention}, คุณได้รับยศแล้ว **buyer Role**.\n"
                    f"📥 โหลดโปรได้เลยที่: [คลิกที่นี่](https://discord.com/channels/923167904629928005/1346807138416328714)",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ **Error:** Role not found. Please contact an admin.", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ **Invalid Key:** คีย์ไม่ถูกต้อง **...** กรุณาลองใหม่!", ephemeral=True
            )

# ทำให้บอทออนไลน์ตลอดเวลา
server_on()

# รันบอท
bot.run(os.getenv('TOKEN'))
