from pyrogram import filters as f
from shared_client import app
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M, LabeledPrice as P, PreCheckoutQuery as Q
from datetime import timedelta as T
from utils.func import add_premium_user as apu
from config import P0, OWNER_ID
import logging

logger = logging.getLogger(__name__)

@app.on_message(f.command("pay") & f.private)
async def p(c, m):
    kb = M([
        [
            B(f"⭐ {P0['d']['l']} - {P0['d']['s']} Star", callback_data="p_d")
        ],
        [
            B(f"⭐ {P0['w']['l']} - {P0['w']['s']} Stars", callback_data="p_w")
        ],
        [
            B(f"⭐ {P0['m']['l']} - {P0['m']['s']} Stars", callback_data="p_m")
        ]
    ])
    
    txt = (
        "💎 **Choose your premium plan:**\n\n"
        f"📅 **{P0['d']['l']}** — {P0['d']['s']} Star\n"
        f"🗓️ **{P0['w']['l']}** — {P0['w']['s']} Stars\n"
        f"📆 **{P0['m']['l']}** — {P0['m']['s']} Stars\n\n"
        "Select a plan below to continue ⤵️"
    )
    await m.reply_text(txt, reply_markup=kb)
    
@app.on_callback_query(f.regex("^p_"))
async def i(c, q):
    pl = q.data.split("_")[1]
    pi = P0[pl]
    try:
        await c.send_invoice(
            chat_id=q.from_user.id,
            title=f"Premium {pi['l']}",
            description=f"{pi['du']} {pi['u']} subscription",
            payload=f"{pl}_{q.from_user.id}",
            currency="XTR",
            prices=[P(label=f"Premium {pi['l']}", amount=pi['s'])]
        )
        await q.answer("Invoice sent 💫")
    except Exception as e:
        logger.error(f"Invoice error: {e}")
        await q.answer(f"Err: {e}", show_alert=True)

@app.on_pre_checkout_query()
async def pc(c, q: Q): 
    await q.answer(ok=True)

@app.on_message(f.successful_payment)
async def sp(c, m):
    p = m.successful_payment
    u = m.from_user.id
    pl = p.invoice_payload.split("_")[0]
    pi = P0[pl]
    
    try:
        logger.info(f"Payment received from user {u}, plan {pl}")
        ok, r = await apu(u, pi['du'], pi['u'])
        
        if ok:
            e = r + T(hours=5, minutes=30)
            d = e.strftime('%d-%b-%Y %I:%M:%S %p')
            await m.reply_text(
                f"✅ **Payment Successful!**\n\n"
                f"💎 Premium {pi['l']} activated!\n"
                f"⭐ Amount: {p.total_amount} Stars\n"
                f"⏰ Valid till: {d} IST\n"
                f"🔖 Transaction ID:\n`{p.telegram_payment_charge_id}`\n\n"
                f"Thank you for your purchase! 🎉"
            )
            logger.info(f"Premium added successfully for user {u}")
            
            # Notify owner
            for o in OWNER_ID:
                try:
                    await c.send_message(o,
                        f"💰 **New Premium Purchase**\n\n"
                        f"👤 User ID: `{u}`\n"
                        f"💎 Plan: {pi['l']}\n"
                        f"⭐ Amount: {p.total_amount} Stars\n"
                        f"🔖 Txn ID: `{p.telegram_payment_charge_id}`\n"
                        f"⏰ Expiry: {d} IST"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify owner {o}: {e}")
        else:
            # Premium activation failed
            await m.reply_text(
                f"⚠️ **Payment Received But Premium Activation Failed**\n\n"
                f"💰 Your {p.total_amount} Stars payment was successful\n"
                f"⚠️ However, premium couldn't be activated automatically\n\n"
                f"📞 **Action Required:**\n"
                f"Contact admin with this transaction ID:\n"
                f"`{p.telegram_payment_charge_id}`\n\n"
                f"Your premium will be activated manually within 24 hours.\n"
                f"Error: `{r}`"
            )
            logger.error(f"Premium activation failed for user {u}: {r}")
            
            # Alert owner with error details
            for o in OWNER_ID:
                try:
                    await c.send_message(o,
                        f"🚨 **PREMIUM ACTIVATION FAILED**\n\n"
                        f"👤 User ID: `{u}`\n"
                        f"💎 Plan: {pi['l']}\n"
                        f"⭐ Amount: {p.total_amount} Stars\n"
                        f"🔖 Txn ID: `{p.telegram_payment_charge_id}`\n"
                        f"❌ Error: `{r}`\n\n"
                        f"**ACTION NEEDED:**\n"
                        f"Use `/add {u}` to manually activate premium"
                    )
                except Exception as e:
                    logger.error(f"Failed to alert owner {o}: {e}")
                    
    except Exception as e:
        logger.exception(f"Critical error in payment handler for user {u}")
        await m.reply_text(
            f"⚠️ **System Error Occurred**\n\n"
            f"Your payment was successful but we encountered a technical issue.\n\n"
            f"📞 Contact admin immediately with this info:\n"
            f"🔖 Transaction ID: `{p.telegram_payment_charge_id}`\n"
            f"👤 Your User ID: `{u}`\n\n"
            f"Premium will be activated manually."
        )
        
        # Critical error notification to owner
        for o in OWNER_ID:
            try:
                await c.send_message(o,
                    f"💥 **CRITICAL PAYMENT ERROR**\n\n"
                    f"👤 User: `{u}`\n"
                    f"🔖 Txn: `{p.telegram_payment_charge_id}`\n"
                    f"⭐ Amount: {p.total_amount} Stars\n"
                    f"❌ Exception: `{str(e)}`\n\n"
                    f"**URGENT:** Manual activation required"
                )
            except Exception as notify_error:
                logger.error(f"Failed to send critical alert: {notify_error}")
