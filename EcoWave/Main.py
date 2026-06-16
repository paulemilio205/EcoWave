# ==================== IMPORTAR LIBRERÍAS ====================
import discord
from discord.ext import commands
import random
import os
import json
from datetime import datetime
import asyncio

# ==================== IMPORTAR TUS ARCHIVOS EXTERNOS ====================
# Estos son tus archivos con las listas
from Retos import retos  # Tu lista de retos
from Tips import tips    # Tu lista de tips
from Datos import datos  # Tu lista de datos curiosos

# ==================== CONFIGURACIÓN DEL BOT ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

# ==================== ARCHIVOS DE DATOS ====================
DATOS_FILE = "datos_usuarios.json"
DUELOS_FILE = "duelos_activos.json"
DIARIO_FILE = "reto_diario.json"
RETOS_ACTUALES_FILE = "retos_actuales.json"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_datos(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Cargar todos los datos
datos_usuarios = cargar_datos(DATOS_FILE)
duelos_activos = cargar_datos(DUELOS_FILE)
reto_diario = cargar_datos(DIARIO_FILE)
retos_actuales = cargar_datos(RETOS_ACTUALES_FILE)

# ==================== SISTEMA DE NIVELES ====================
def obtener_nivel(retos_completados):
    if retos_completados >= 50:
        return {"nombre": "🏆 LEYENDA ECOLÓGICA", "color": 0xf1c40f}
    elif retos_completados >= 30:
        return {"nombre": "💚 GUARDIÁN DEL PLANETA", "color": 0x1abc9c}
    elif retos_completados >= 15:
        return {"nombre": "🍃 ECO-WARRIOR", "color": 0x27ae60}
    elif retos_completados >= 5:
        return {"nombre": "🌱 APRENDIZ VERDE", "color": 0x2ecc71}
    else:
        return {"nombre": "🦋 EXPLORADOR AMBIENTAL", "color": 0x3498db}

# ==================== SISTEMA DE INSIGNIAS ====================
def verificar_insignias(retos_completados, racha, duelos_ganados, insignias_actuales):
    nuevas_insignias = []
    
    insignias_disponibles = {
        1: ("🌱 Primer Reto", "retos"),
        5: ("🎯 Eco-Constante", "retos"),
        10: ("💪 Eco-Dedicado", "retos"),
        20: ("⭐ Eco-Maestro", "retos"),
        30: ("👑 Eco-Leyenda", "retos"),
        50: ("🏆 Eco-Dios", "retos"),
        7: ("🔥 Racha de Fuego", "racha"),
        30: ("⚡ Imparable", "racha"),
        3: ("⚔️ Duelista", "duelos"),
        5: ("🏅 Campeón", "duelos")
    }
    
    for req, (nombre, tipo) in insignias_disponibles.items():
        if tipo == "retos" and retos_completados >= req and req not in insignias_actuales:
            nuevas_insignias.append(nombre)
            insignias_actuales.append(req)
        elif tipo == "racha" and racha >= req and req not in insignias_actuales:
            nuevas_insignias.append(nombre)
            insignias_actuales.append(req)
        elif tipo == "duelos" and duelos_ganados >= req and req not in insignias_actuales:
            nuevas_insignias.append(nombre)
            insignias_actuales.append(req)
    
    return nuevas_insignias, insignias_actuales

# ==================== CLASE PARA ENCUESTA DE RETO NORMAL ====================
class EncuestaView(discord.ui.View):
    def __init__(self, reto, usuario_id, usuario_nombre):
        super().__init__(timeout=60.0)
        self.reto = reto
        self.usuario_id = usuario_id
        self.usuario_nombre = usuario_nombre
        self.votos_si = []
        self.votos_no = []
        self.message = None
    
    @discord.ui.button(label="✅ Sí, lo completó", style=discord.ButtonStyle.success)
    async def si_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id == self.usuario_id:
            await interaction.response.send_message("❌ No puedes votar en tu propia encuesta.", ephemeral=True)
            return
        
        if user_id in self.votos_si:
            await interaction.response.send_message("❌ Ya votaste 'Sí' a esta encuesta.", ephemeral=True)
            return
        if user_id in self.votos_no:
            self.votos_no.remove(user_id)
        
        self.votos_si.append(user_id)
        await interaction.response.send_message(f"✅ Votaste que {self.usuario_nombre} completó el reto", ephemeral=True)
        await self.actualizar_mensaje(interaction)
    
    @discord.ui.button(label="❌ No, no lo completó", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id == self.usuario_id:
            await interaction.response.send_message("❌ No puedes votar en tu propia encuesta.", ephemeral=True)
            return
        
        if user_id in self.votos_no:
            await interaction.response.send_message("❌ Ya votaste 'No' a esta encuesta.", ephemeral=True)
            return
        if user_id in self.votos_si:
            self.votos_si.remove(user_id)
        
        self.votos_no.append(user_id)
        await interaction.response.send_message(f"❌ Votaste que {self.usuario_nombre} NO completó el reto", ephemeral=True)
        await self.actualizar_mensaje(interaction)
    
    async def actualizar_mensaje(self, interaction):
        total_votos = len(self.votos_si) + len(self.votos_no)
        
        embed = discord.Embed(
            title="📊 ENCUESTA DE VERIFICACIÓN",
            description=f"**{self.usuario_nombre}** completó el reto:\n*{self.reto}*",
            color=discord.Color.blue()
        )
        embed.add_field(name="✅ Sí", value=f"{len(self.votos_si)} votos", inline=True)
        embed.add_field(name="❌ No", value=f"{len(self.votos_no)} votos", inline=True)
        embed.add_field(name="📊 Total", value=f"{total_votos} votos", inline=True)
        embed.set_footer(text=f"La votación termina en {int(self.timeout)} segundos")
        
        await interaction.message.edit(embed=embed, view=self)
    
    async def on_timeout(self):
        total_votos = len(self.votos_si) + len(self.votos_no)
        
        if total_votos == 0:
            await self.felicitar_usuario("✅ No hubo votos, reto validado automáticamente")
            return
        
        if len(self.votos_si) > len(self.votos_no):
            await self.felicitar_usuario(f"✅ Mayoría de votos SÍ ({len(self.votos_si)} vs {len(self.votos_no)})")
        elif len(self.votos_si) == len(self.votos_no):
            await self.felicitar_usuario(f"🤝 Empate en la votación ({len(self.votos_si)} vs {len(self.votos_no)}), reto validado")
        else:
            await self.rechazar_reto(f"❌ Mayoría de votos NO ({len(self.votos_no)} vs {len(self.votos_si)})")
    
    async def felicitar_usuario(self, motivo):
        global datos_usuarios
        
        if self.usuario_id not in datos_usuarios:
            datos_usuarios[self.usuario_id] = {
                "nombre": self.usuario_nombre,
                "retos_completados": 0,
                "racha": 0,
                "mejor_racha": 0,
                "duelos_ganados": 0,
                "ultimo_reto": None,
                "insignias": []
            }
        
        datos_usuarios[self.usuario_id]["retos_completados"] += 1
        
        hoy = datetime.now().date()
        ultimo = datos_usuarios[self.usuario_id].get("ultimo_reto")
        
        if ultimo:
            try:
                ultimo_date = datetime.fromisoformat(ultimo).date()
                diferencia = (hoy - ultimo_date).days
                
                if diferencia == 1:
                    datos_usuarios[self.usuario_id]["racha"] += 1
                elif diferencia > 1:
                    datos_usuarios[self.usuario_id]["racha"] = 1
            except:
                datos_usuarios[self.usuario_id]["racha"] = 1
        else:
            datos_usuarios[self.usuario_id]["racha"] = 1
        
        racha_actual = datos_usuarios[self.usuario_id]["racha"]
        if racha_actual > datos_usuarios[self.usuario_id].get("mejor_racha", 0):
            datos_usuarios[self.usuario_id]["mejor_racha"] = racha_actual
        
        datos_usuarios[self.usuario_id]["ultimo_reto"] = hoy.isoformat()
        
        retos_total = datos_usuarios[self.usuario_id]["retos_completados"]
        duelos_ganados = datos_usuarios[self.usuario_id].get("duelos_ganados", 0)
        insignias_actuales = datos_usuarios[self.usuario_id].get("insignias", [])
        nuevas_insignias, insignias_actuales = verificar_insignias(retos_total, racha_actual, duelos_ganados, insignias_actuales)
        datos_usuarios[self.usuario_id]["insignias"] = insignias_actuales
        
        semana_actual = datetime.now().isocalendar()[1]
        if datos_usuarios[self.usuario_id].get("semana") != semana_actual:
            datos_usuarios[self.usuario_id]["semana"] = semana_actual
            datos_usuarios[self.usuario_id]["retos_semana"] = 1
        else:
            datos_usuarios[self.usuario_id]["retos_semana"] = datos_usuarios[self.usuario_id].get("retos_semana", 0) + 1
        
        guardar_datos(DATOS_FILE, datos_usuarios)
        
        nivel = obtener_nivel(retos_total)
        
        embed = discord.Embed(
            title="🎉 ¡FELICITACIONES! 🎉",
            description=f"{self.usuario_nombre} ha completado un reto ecológico",
            color=nivel["color"]
        )
        embed.add_field(name="✅ Reto completado", value=f"*{self.reto}*", inline=False)
        embed.add_field(name="🏆 Total retos", value=f"{retos_total}", inline=True)
        embed.add_field(name="🔥 Racha actual", value=f"{racha_actual} días", inline=True)
        embed.add_field(name="📊 Nivel", value=nivel["nombre"], inline=True)
        embed.add_field(name="📋 Votación", value=motivo, inline=False)
        
        if nuevas_insignias:
            embed.add_field(name="🎖️ NUEVAS INSIGNIAS", value="\n".join(nuevas_insignias), inline=False)
        
        canal = self.message.channel
        await canal.send(f"🎉 ¡ENHORABUENA <@{self.usuario_id}>! 🎉", embed=embed)
        
        try:
            usuario = await bot.fetch_user(int(self.usuario_id))
            await usuario.send(f"🎉 ¡Felicidades! Completaste el reto: **{self.reto}**\nTotal: {retos_total} retos\n{motivo}")
        except:
            pass
        
        embed_final = discord.Embed(
            title="📊 ENCUESTA FINALIZADA",
            description=f"**{self.usuario_nombre}** completó el reto:\n*{self.reto}*",
            color=discord.Color.green()
        )
        embed_final.add_field(name="✅ Resultado", value="¡RETO VALIDADO! +1 punto", inline=False)
        embed_final.add_field(name="✅ Sí", value=f"{len(self.votos_si)} votos", inline=True)
        embed_final.add_field(name="❌ No", value=f"{len(self.votos_no)} votos", inline=True)
        
        await self.message.edit(embed=embed_final, view=None)
    
    async def rechazar_reto(self, motivo):
        embed = discord.Embed(
            title="❌ RETO NO VALIDADO",
            description=f"{self.usuario_nombre} intentó completar el reto:\n*{self.reto}*",
            color=discord.Color.red()
        )
        embed.add_field(name="📊 Resultado de la votación", 
                       value=f"✅ Sí: {len(self.votos_si)} votos | ❌ No: {len(self.votos_no)} votos", 
                       inline=False)
        embed.add_field(name="💡 Motivo", value=motivo, inline=False)
        embed.add_field(name="🌱 Ánimo", value="¡No te rindas! Puedes intentarlo de nuevo con `$Reto`", inline=False)
        
        canal = self.message.channel
        await canal.send(embed=embed)
        
        embed_final = discord.Embed(
            title="📊 ENCUESTA FINALIZADA",
            description=f"**{self.usuario_nombre}** completó el reto:\n*{self.reto}*",
            color=discord.Color.red()
        )
        embed_final.add_field(name="❌ Resultado", value="RETO RECHAZADO - No se sumaron puntos", inline=False)
        embed_final.add_field(name="✅ Sí", value=f"{len(self.votos_si)} votos", inline=True)
        embed_final.add_field(name="❌ No", value=f"{len(self.votos_no)} votos", inline=True)
        
        await self.message.edit(embed=embed_final, view=None)
        
        try:
            usuario = await bot.fetch_user(int(self.usuario_id))
            await usuario.send(f"❌ Tu reto **{self.reto}** no fue validado.\n{motivo}\n¡No te desanimes, inténtalo de nuevo con `$Reto`!")
        except:
            pass

# ==================== CLASE PARA ENCUESTA DE DUELO ====================
class DueloEncuestaView(discord.ui.View):
    def __init__(self, reto, jugador1_id, jugador2_id, jugador1_nombre, jugador2_nombre, duelo_id):
        super().__init__(timeout=60.0)
        self.reto = reto
        self.jugador1_id = jugador1_id
        self.jugador2_id = jugador2_id
        self.jugador1_nombre = jugador1_nombre
        self.jugador2_nombre = jugador2_nombre
        self.duelo_id = duelo_id
        self.votos_jugador1 = []
        self.votos_jugador2 = []
        self.message = None
        
        self.children[0].label = f"🥇 {jugador1_nombre}"
        self.children[1].label = f"🥈 {jugador2_nombre}"
    
    @discord.ui.button(label="", style=discord.ButtonStyle.success, row=0)
    async def jugador1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id == self.jugador1_id or user_id == self.jugador2_id:
            await interaction.response.send_message("❌ Los participantes no pueden votar en su propio duelo.", ephemeral=True)
            return
        
        if user_id in self.votos_jugador1:
            await interaction.response.send_message(f"❌ Ya votaste por {self.jugador1_nombre}", ephemeral=True)
            return
        
        if user_id in self.votos_jugador2:
            self.votos_jugador2.remove(user_id)
        
        self.votos_jugador1.append(user_id)
        await interaction.response.send_message(f"✅ Votaste por {self.jugador1_nombre}", ephemeral=True)
        await self.actualizar_mensaje(interaction)
    
    @discord.ui.button(label="", style=discord.ButtonStyle.primary, row=0)
    async def jugador2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id == self.jugador1_id or user_id == self.jugador2_id:
            await interaction.response.send_message("❌ Los participantes no pueden votar en su propio duelo.", ephemeral=True)
            return
        
        if user_id in self.votos_jugador2:
            await interaction.response.send_message(f"❌ Ya votaste por {self.jugador2_nombre}", ephemeral=True)
            return
        
        if user_id in self.votos_jugador1:
            self.votos_jugador1.remove(user_id)
        
        self.votos_jugador2.append(user_id)
        await interaction.response.send_message(f"✅ Votaste por {self.jugador2_nombre}", ephemeral=True)
        await self.actualizar_mensaje(interaction)
    
    async def actualizar_mensaje(self, interaction):
        total_votos = len(self.votos_jugador1) + len(self.votos_jugador2)
        
        embed = discord.Embed(
            title="⚔️ ENCUESTA DE DUELO",
            description=f"**¿Quién completó mejor el reto?**\n*{self.reto}*",
            color=discord.Color.purple()
        )
        embed.add_field(name=f"🥇 {self.jugador1_nombre}", value=f"{len(self.votos_jugador1)} votos", inline=True)
        embed.add_field(name=f"🥈 {self.jugador2_nombre}", value=f"{len(self.votos_jugador2)} votos", inline=True)
        embed.add_field(name="📊 Total", value=f"{total_votos} votos", inline=True)
        embed.set_footer(text=f"La votación termina en {int(self.timeout)} segundos")
        
        await interaction.message.edit(embed=embed, view=self)
    
    async def on_timeout(self):
        global datos_usuarios
        
        total_votos = len(self.votos_jugador1) + len(self.votos_jugador2)
        
        # Caso 1: Sin votos - Nadie gana
        if total_votos == 0:
            embed = discord.Embed(
                title="⚔️ DUELO FINALIZADO",
                description=f"**{self.jugador1_nombre}** vs **{self.jugador2_nombre}**",
                color=discord.Color.red()
            )
            embed.add_field(name="❌ Resultado", value="No hubo votos - Nadie gana", inline=False)
            await self.message.edit(embed=embed, view=None)
            
            if self.duelo_id in duelos_activos:
                del duelos_activos[self.duelo_id]
                guardar_datos(DUELOS_FILE, duelos_activos)
            return
        
        # Caso 2: Ganó jugador 1
        if len(self.votos_jugador1) > len(self.votos_jugador2):
            ganador_id = self.jugador1_id
            ganador_nombre = self.jugador1_nombre
            perdedor_nombre = self.jugador2_nombre
            color = discord.Color.gold()
        
        # Caso 3: Ganó jugador 2
        elif len(self.votos_jugador2) > len(self.votos_jugador1):
            ganador_id = self.jugador2_id
            ganador_nombre = self.jugador2_nombre
            perdedor_nombre = self.jugador1_nombre
            color = discord.Color.gold()
        
        # Caso 4: Empate - Nadie gana puntos extra
        else:
            embed = discord.Embed(
                title="⚔️ DUELO FINALIZADO",
                description=f"**{self.jugador1_nombre}** vs **{self.jugador2_nombre}**",
                color=discord.Color.orange()
            )
            embed.add_field(name="🤝 Resultado", value="¡EMPATE! Nadie gana puntos extra", inline=False)
            embed.add_field(name=f"🥇 {self.jugador1_nombre}", value=f"{len(self.votos_jugador1)} votos", inline=True)
            embed.add_field(name=f"🥈 {self.jugador2_nombre}", value=f"{len(self.votos_jugador2)} votos", inline=True)
            await self.message.edit(embed=embed, view=None)
            
            if self.duelo_id in duelos_activos:
                del duelos_activos[self.duelo_id]
                guardar_datos(DUELOS_FILE, duelos_activos)
            return
        
        # ========== DAR RECOMPENSA AL GANADOR ==========
        if ganador_id not in datos_usuarios:
            datos_usuarios[ganador_id] = {
                "nombre": ganador_nombre,
                "retos_completados": 0,
                "racha": 0,
                "mejor_racha": 0,
                "duelos_ganados": 0,
                "ultimo_reto": None,
                "insignias": []
            }
        
        # El ganador recibe 1 punto extra
        datos_usuarios[ganador_id]["retos_completados"] += 1
        datos_usuarios[ganador_id]["duelos_ganados"] = datos_usuarios[ganador_id].get("duelos_ganados", 0) + 1
        
        # Verificar insignias por duelos
        duelos_ganados = datos_usuarios[ganador_id]["duelos_ganados"]
        insignias_actuales = datos_usuarios[ganador_id].get("insignias", [])
        
        if duelos_ganados >= 3 and 3 not in insignias_actuales:
            insignias_actuales.append(3)
            await self.enviar_notificacion_insignia(ganador_id, "⚔️ Duelista")
        if duelos_ganados >= 5 and 5 not in insignias_actuales:
            insignias_actuales.append(5)
            await self.enviar_notificacion_insignia(ganador_id, "🏅 Campeón")
        
        datos_usuarios[ganador_id]["insignias"] = insignias_actuales
        guardar_datos(DATOS_FILE, datos_usuarios)
        
        # Mensaje de victoria
        embed = discord.Embed(
            title="🏆 ¡DUELO FINALIZADO! 🏆",
            description=f"**{ganador_nombre}** ha ganado el duelo ecológico",
            color=color
        )
        embed.add_field(name="🌍 Reto", value=f"*{self.reto}*", inline=False)
        embed.add_field(name="🥇 Ganador", value=f"{ganador_nombre}", inline=True)
        embed.add_field(name="📊 Votación", value=f"{len(self.votos_jugador1)} - {len(self.votos_jugador2)}", inline=True)
        embed.add_field(name="🌟 Recompensa", value="¡+1 punto extra por ganar el duelo!", inline=False)
        
        await self.message.channel.send(f"🎉 ¡ENHORABUENA <@{ganador_id}>! 🎉", embed=embed)
        
        # Mostrar resultado en el mensaje de la encuesta
        embed_final = discord.Embed(
            title="⚔️ ENCUESTA DE DUELO FINALIZADA",
            description=f"**{ganador_nombre}** ganó con {len(self.votos_jugador1) if ganador_id == self.jugador1_id else len(self.votos_jugador2)} votos",
            color=color
        )
        await self.message.edit(embed=embed_final, view=None)
        
        # Eliminar duelo de la lista de activos
        if self.duelo_id in duelos_activos:
            del duelos_activos[self.duelo_id]
            guardar_datos(DUELOS_FILE, duelos_activos)
    
    async def enviar_notificacion_insignia(self, user_id, nombre_insignia):
        try:
            usuario = await bot.fetch_user(int(user_id))
            await usuario.send(f"🏅 ¡Has desbloqueado la insignia **{nombre_insignia}** por ganar duelos!")
        except:
            pass

# ==================== COMANDOS PRINCIPALES ====================

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"📊 Usuarios registrados: {len(datos_usuarios)}")
    print(f"⚔️ Duelos activos: {len(duelos_activos)}")
    print(f"📅 Retos diarios: {len(reto_diario)}")
    print(f"🎯 Retos actuales: {len(retos_actuales)}")
    print(f"📋 Retos cargados desde archivo: {len(retos)}")
    print(f"💡 Tips cargados desde archivo: {len(tips)}")
    print(f"📊 Datos cargados desde archivo: {len(datos)}")

@bot.command()
async def Hola(ctx):
    await ctx.send(f"¡Hola {ctx.author.mention}! 👋 ¿Listo para salvar el planeta? Usa `$Reto`")

@bot.command()
async def Reto(ctx):
    """Te da un reto ecológico de tu archivo Retos.py"""
    user_id = str(ctx.author.id)
    reto = random.choice(retos)  # Usa tu lista de retos
    
    if user_id not in datos_usuarios:
        datos_usuarios[user_id] = {
            "nombre": ctx.author.name,
            "retos_completados": 0,
            "racha": 0,
            "mejor_racha": 0,
            "duelos_ganados": 0,
            "ultimo_reto": None,
            "insignias": []
        }
        guardar_datos(DATOS_FILE, datos_usuarios)
    
    retos_actuales[user_id] = reto
    guardar_datos(RETOS_ACTUALES_FILE, retos_actuales)
    
    embed = discord.Embed(
        title="🌍 NUEVO RETO ECOLÓGICO",
        description=f"**{ctx.author.display_name}**",
        color=0x2ecc71
    )
    embed.add_field(name="📋 Tu reto:", value=f"*{reto}*", inline=False)
    embed.add_field(name="✅ Para completarlo:", value="Usa `$Encuesta` cuando termines", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def Encuesta(ctx):
    """Crea una encuesta para verificar tu reto"""
    user_id = str(ctx.author.id)
    
    if user_id not in retos_actuales:
        await ctx.send(f"{ctx.author.mention} primero usa `$Reto` para obtener un reto.")
        return
    
    reto_completado = retos_actuales[user_id]
    del retos_actuales[user_id]
    guardar_datos(RETOS_ACTUALES_FILE, retos_actuales)
    
    embed = discord.Embed(
        title="📊 ENCUESTA DE VERIFICACIÓN",
        description=f"**{ctx.author.display_name}** completó el reto:\n*{reto_completado}*",
        color=discord.Color.blue()
    )
    embed.add_field(name="✅ Sí", value="0 votos", inline=True)
    embed.add_field(name="❌ No", value="0 votos", inline=True)
    embed.add_field(name="⏰ Tiempo", value="60 segundos para votar", inline=True)
    embed.set_footer(text="¡Vota usando los botones abajo! | Se valida con SÍ, empate o sin votos")
    
    view = EncuestaView(reto_completado, user_id, ctx.author.display_name)
    message = await ctx.send(embed=embed, view=view)
    view.message = message
    
    await ctx.send(f"✅ Encuesta creada para verificar el reto de {ctx.author.mention}")

@bot.command()
async def Duelo(ctx, oponente: discord.Member):
    """Reta a alguien a un duelo"""
    if oponente == ctx.author:
        await ctx.send("❌ No puedes duelar contigo mismo")
        return
    
    if oponente.bot:
        await ctx.send("❌ No puedes duelar con bots")
        return
    
    jugador1_id = str(ctx.author.id)
    jugador2_id = str(oponente.id)
    
    if jugador1_id not in datos_usuarios:
        datos_usuarios[jugador1_id] = {
            "nombre": ctx.author.name,
            "retos_completados": 0,
            "racha": 0,
            "mejor_racha": 0,
            "duelos_ganados": 0,
            "ultimo_reto": None,
            "insignias": []
        }
    
    if jugador2_id not in datos_usuarios:
        datos_usuarios[jugador2_id] = {
            "nombre": oponente.name,
            "retos_completados": 0,
            "racha": 0,
            "mejor_racha": 0,
            "duelos_ganados": 0,
            "ultimo_reto": None,
            "insignias": []
        }
    
    guardar_datos(DATOS_FILE, datos_usuarios)
    
    reto = random.choice(retos)
    duelo_id = f"{jugador1_id}_{jugador2_id}_{datetime.now().timestamp()}"
    
    duelos_activos[duelo_id] = {
        "reto": reto,
        "jugador1": jugador1_id,
        "jugador2": jugador2_id,
        "fecha": datetime.now().isoformat(),
        "completado_por": []
    }
    guardar_datos(DUELOS_FILE, duelos_activos)
    
    embed = discord.Embed(
        title="⚔️ ¡DUELO ECOLÓGICO! ⚔️",
        description=f"{ctx.author.mention} vs {oponente.mention}",
        color=0xe74c3c
    )
    embed.add_field(name="🌍 Reto del duelo", value=f"*{reto}*", inline=False)
    embed.add_field(name="⏰ Tiempo", value="24 horas para completar el reto", inline=True)
    embed.add_field(name="📝 Cómo participar", value="1. Cada uno completa el reto por su cuenta\n2. Usan `$CompletarDuelo` cuando terminen\n3. La comunidad votará al ganador", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def CompletarDuelo(ctx):
    """Marca que completaste tu parte del duelo"""
    user_id = str(ctx.author.id)
    
    duelo_encontrado = None
    duelo_id = None
    
    for did, duelo in duelos_activos.items():
        if user_id == duelo["jugador1"] or user_id == duelo["jugador2"]:
            duelo_encontrado = duelo
            duelo_id = did
            break
    
    if not duelo_encontrado:
        await ctx.send(f"{ctx.author.mention} no tienes duelos activos. Usa `$Duelo @usuario` para crear uno.")
        return
    
    if user_id in duelo_encontrado["completado_por"]:
        await ctx.send(f"{ctx.author.mention} ya marcaste este duelo como completado.")
        return
    
    duelo_encontrado["completado_por"].append(user_id)
    guardar_datos(DUELOS_FILE, duelos_activos)
    
    # Verificar cuántos han completado
    completados = len(duelo_encontrado["completado_por"])
    
    if completados == 1:
        # Solo uno completó
        otro_jugador = duelo_encontrado["jugador1"] if duelo_encontrado["jugador1"] != user_id else duelo_encontrado["jugador2"]
        otro_user = await bot.fetch_user(int(otro_jugador))
        await ctx.send(f"✅ {ctx.author.mention} has completado tu parte del duelo. Esperando a que {otro_user.display_name} complete la suya.")
    
    elif completados == 2:
        # Ambos completaron - CREAR ENCUESTA
        jugador1_id = duelo_encontrado["jugador1"]
        jugador2_id = duelo_encontrado["jugador2"]
        
        jugador1 = await bot.fetch_user(int(jugador1_id))
        jugador2 = await bot.fetch_user(int(jugador2_id))
        
        # Crear embed de votación
        embed = discord.Embed(
            title="⚔️ VOTACIÓN DEL DUELO",
            description=f"**¿Quién completó mejor el reto?**\n*{duelo_encontrado['reto']}*",
            color=discord.Color.purple()
        )
        embed.add_field(name=f"🥇 {jugador1.display_name}", value="0 votos", inline=True)
        embed.add_field(name=f"🥈 {jugador2.display_name}", value="0 votos", inline=True)
        embed.add_field(name="⏰ Tiempo", value="60 segundos para votar", inline=True)
        embed.set_footer(text="¡Vota por el ganador! La comunidad decide quién merece el punto extra")
        
        # Crear vista con botones
        view = DueloEncuestaView(
            duelo_encontrado["reto"],
            jugador1_id, jugador2_id,
            jugador1.display_name, jugador2.display_name,
            duelo_id
        )
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        
        await ctx.send(f"✅ ¡Ambos completaron el duelo! La comunidad votará al ganador en 60 segundos.")
        print(f"📢 Duelo {duelo_id} - Ambos completaron, encuesta creada")

@bot.command()
async def RetoDiario(ctx):
    """Reto especial que solo puedes hacer una vez al día"""
    user_id = str(ctx.author.id)
    hoy = datetime.now().date().isoformat()
    
    if user_id in reto_diario:
        if reto_diario[user_id].get("fecha") == hoy and reto_diario[user_id].get("completado", False):
            await ctx.send(f"❌ {ctx.author.mention} ya completaste tu reto diario hoy. ¡Vuelve mañana!")
            return
    
    reto = random.choice(retos)
    reto_diario[user_id] = {
        "reto": reto,
        "fecha": hoy,
        "completado": False
    }
    guardar_datos(DIARIO_FILE, reto_diario)
    
    retos_actuales[user_id] = reto
    guardar_datos(RETOS_ACTUALES_FILE, retos_actuales)
    
    embed = discord.Embed(
        title="📅 RETO DIARIO",
        description=f"**{ctx.author.display_name}**",
        color=0x9b59b6
    )
    embed.add_field(name="⭐ Tu reto especial:", value=f"*{reto}*", inline=False)
    embed.add_field(name="🏆 Recompensa", value="¡Ganas 2 puntos en lugar de 1!", inline=True)
    embed.add_field(name="✅ Para completarlo", value="Usa `$Encuesta` cuando termines", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def Perfil(ctx, miembro: discord.Member = None):
    """Muestra el perfil completo"""
    if miembro is None:
        miembro = ctx.author
    
    user_id = str(miembro.id)
    
    if user_id not in datos_usuarios:
        await ctx.send(f"{miembro.display_name} aún no tiene perfil. Usa `$Reto` para comenzar.")
        return
    
    datos = datos_usuarios[user_id]
    retos_total = datos.get("retos_completados", 0)
    racha = datos.get("racha", 0)
    mejor_racha = datos.get("mejor_racha", 0)
    duelos_ganados = datos.get("duelos_ganados", 0)
    nivel = obtener_nivel(retos_total)
    
    nombres_insignias = {
        1: "🌱 Primer Reto", 5: "🎯 Eco-Constante", 10: "💪 Eco-Dedicado",
        20: "⭐ Eco-Maestro", 30: "👑 Eco-Leyenda", 50: "🏆 Eco-Dios",
        7: "🔥 Racha de Fuego", 30: "⚡ Imparable",
        3: "⚔️ Duelista", 5: "🏅 Campeón"
    }
    
    insignias = datos.get("insignias", [])
    texto_insignias = [nombres_insignias.get(i, "?") for i in insignias if i in nombres_insignias]
    
    embed = discord.Embed(
        title=f"🌿 Perfil Ecológico de {miembro.display_name}",
        color=nivel["color"]
    )
    if miembro.avatar:
        embed.set_thumbnail(url=miembro.avatar.url)
    
    embed.add_field(name="📊 Nivel", value=nivel["nombre"], inline=True)
    embed.add_field(name="🏆 Retos", value=f"{retos_total}", inline=True)
    embed.add_field(name="🔥 Racha", value=f"{racha} días", inline=True)
    embed.add_field(name="⭐ Mejor racha", value=f"{mejor_racha} días", inline=True)
    embed.add_field(name="⚔️ Duelos ganados", value=f"{duelos_ganados}", inline=True)
    
    if texto_insignias:
        embed.add_field(name="🎖️ Insignias", value="\n".join(texto_insignias[:5]), inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def Ranking(ctx):
    """Ranking general"""
    if not datos_usuarios:
        await ctx.send("📊 Aún no hay datos. ¡Usa `$Reto`!")
        return
    
    ranking = []
    for uid, datos in datos_usuarios.items():
        nombre = datos.get("nombre", "Usuario")
        retos_val = datos.get("retos_completados", 0)
        ranking.append((nombre, retos_val))
    
    ranking.sort(key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(title="🏆 RANKING ECOLÓGICO", color=0xf1c40f)
    for i, (nombre, retos_val) in enumerate(ranking[:10], 1):
        if i == 1:
            medalla = "🥇"
        elif i == 2:
            medalla = "🥈"
        elif i == 3:
            medalla = "🥉"
        else:
            medalla = "📌"
        embed.add_field(name=f"{medalla} {i}. {nombre}", value=f"{retos_val} retos", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def Racha(ctx):
    """Muestra tu racha"""
    user_id = str(ctx.author.id)
    if user_id not in datos_usuarios:
        await ctx.send(f"{ctx.author.mention} aún no tienes racha.")
        return
    
    racha = datos_usuarios[user_id].get("racha", 0)
    mejor = datos_usuarios[user_id].get("mejor_racha", 0)
    
    emoji = "🔥" if racha >= 7 else "🌱"
    embed = discord.Embed(title=f"{emoji} Racha de {ctx.author.display_name}", color=0xe67e22)
    embed.add_field(name="Actual", value=f"{racha} días", inline=True)
    embed.add_field(name="Mejor", value=f"{mejor} días", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def Insignias(ctx, miembro: discord.Member = None):
    """Muestra insignias"""
    if miembro is None:
        miembro = ctx.author
    
    user_id = str(miembro.id)
    if user_id not in datos_usuarios:
        await ctx.send(f"{miembro.display_name} no tiene insignias.")
        return
    
    nombres = {1: "🌱 Primer Reto", 5: "🎯 Eco-Constante", 10: "💪 Eco-Dedicado",
               20: "⭐ Eco-Maestro", 30: "👑 Eco-Leyenda", 50: "🏆 Eco-Dios",
               7: "🔥 Racha de Fuego", 30: "⚡ Imparable", 3: "⚔️ Duelista", 5: "🏅 Campeón"}
    
    insignias = datos_usuarios[user_id].get("insignias", [])
    texto = [nombres.get(i, "?") for i in insignias if i in nombres]
    
    embed = discord.Embed(title=f"🎖️ Insignias de {miembro.display_name}", 
                          description="\n".join(texto) if texto else "Ninguna aún",
                          color=0xf1c40f)
    await ctx.send(embed=embed)

@bot.command()
async def Progreso(ctx):
    """Gráfico de progreso"""
    user_id = str(ctx.author.id)
    if user_id not in datos_usuarios:
        await ctx.send(f"{ctx.author.mention} usa `$Reto` para comenzar.")
        return
    
    retos_val = datos_usuarios[user_id].get("retos_completados", 0)
    
    if retos_val < 5:
        siguiente, actual = 5, 0
        nombre_nivel = "Aprendiz Verde"
    elif retos_val < 15:
        siguiente, actual = 15, 5
        nombre_nivel = "Eco-Warrior"
    elif retos_val < 30:
        siguiente, actual = 30, 15
        nombre_nivel = "Guardian del Planeta"
    elif retos_val < 50:
        siguiente, actual = 50, 30
        nombre_nivel = "Maestro Ecológico"
    else:
        await ctx.send(f"🏆 ¡{ctx.author.mention} has alcanzado el NIVEL MÁXIMO!")
        return
    
    progreso = retos_val - actual
    total = siguiente - actual
    porcentaje = int((progreso / total) * 20)
    barra = "🟩" * porcentaje + "⬜" * (20 - porcentaje)
    
    embed = discord.Embed(title=f"📈 Progreso de {ctx.author.display_name}", color=0x3498db)
    embed.add_field(name=f"Para llegar a {nombre_nivel}", 
                    value=f"{barra}\n{progreso}/{total} retos ({porcentaje*5}%)", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def TopSemanal(ctx):
    """Ranking semanal"""
    semana_actual = datetime.now().isocalendar()[1]
    ranking = []
    
    for uid, datos in datos_usuarios.items():
        if datos.get("semana") == semana_actual:
            retos_semana = datos.get("retos_semana", 0)
            if retos_semana > 0:
                nombre = datos.get("nombre", "Usuario")
                ranking.append((nombre, retos_semana))
    
    if not ranking:
        await ctx.send("📊 Sin actividad esta semana.")
        return
    
    ranking.sort(key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title=f"🏆 TOP SEMANAL - Semana #{semana_actual}", color=0x1abc9c)
    for i, (nombre, retos_val) in enumerate(ranking[:5], 1):
        embed.add_field(name=f"{i}. {nombre}", value=f"{retos_val} retos", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def Meme(ctx):
    try:
        if not os.path.exists("memes"):
            os.makedirs("memes")
        memes = os.listdir("memes")
        if memes:
            meme = random.choice(memes)
            with open(f"memes/{meme}", "rb") as f:
                await ctx.send(file=discord.File(f))
        else:
            await ctx.send("📭 Agrega memes a la carpeta 'memes'")
    except Exception as e:
        await ctx.send(f"📭 Error: {e}")

@bot.command()
async def Tip(ctx):
    """Usa tu lista de tips del archivo Tips.py"""
    await ctx.send(f"💡 {random.choice(tips)}")

@bot.command()
async def Dato(ctx):
    """Usa tu lista de datos del archivo Datos.py"""
    await ctx.send(f"📊 {random.choice(datos)}")

@bot.command()
async def Ayuda(ctx):
    """Muestra todos los comandos disponibles"""
    embed = discord.Embed(title="🤖 COMANDOS DEL BOT ECOLÓGICO", description="¡Ayuda al planeta!", color=0x3498db)
    embed.add_field(name="🎯 RETOS", 
                    value="$Reto - Obtener un reto\n$Encuesta - Verificar tu reto\n$RetoDiario - Reto especial del día", 
                    inline=False)
    embed.add_field(name="⚔️ DUELOS", 
                    value="$Duelo @usuario - Retar a alguien\n$CompletarDuelo - Marcar que completaste tu parte", 
                    inline=False)
    embed.add_field(name="📊 PERFIL", 
                    value="$Perfil - Ver tu perfil\n$Ranking - Ver ranking general\n$Racha - Ver tu racha\n$Insignias - Ver tus logros\n$Progreso - Ver gráfico de progreso\n$TopSemanal - Top de la semana", 
                    inline=False)
    embed.add_field(name="ℹ️ OTROS", 
                    value="$Hola - Saludo\n$Meme - Meme ecológico\n$Tip - Consejo ecológico\n$Dato - Dato curioso\n$Ayuda - Este mensaje", 
                    inline=False)
    await ctx.send(embed=embed)

# ==================== EJECUTAR EL BOT ====================
TOKEN = "TU_TOKEN_A"
bot.run(TOKEN)