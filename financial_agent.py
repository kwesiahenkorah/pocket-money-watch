import json
import os
from datetime import datetime
import asyncio

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class FinancialAgent(Agent):

    class FinancialBehaviour(CyclicBehaviour):

        async def run(self):
            user_input = input("\nYou: ")

            perception = self.perceive(user_input)
            action = self.decide(perception)
            await self.act(action, user_input) 

        # PERCEIVE
        def perceive(self, user_input):
            return user_input.lower()

        # DECIDE 
        def decide(self, perception):
            if "income" in perception:
                return "add_income"
            elif "spent" in perception or "spend" in perception:
                return "add_expense"
            elif "balance" in perception:
                return "check_balance"
            elif "predict" in perception:
                return "predict"
            elif "summary" in perception:
                return "summary"
            elif "insight" in perception or "insights" in perception:
                return "insights"
            elif "help" in perception:
                return "help"
            elif "exit" in perception or "quit" in perception:
                return "exit"
            else:
                return "unknown"

        # ACT 
        async def act(self, action, user_input):
            if action == "add_income":
                self.agent.add_income(user_input)
            elif action == "add_expense":
                self.agent.add_expense(user_input)
            elif action == "check_balance":
                print(f"💰 Balance: GHS {self.agent.beliefs['balance']}")
            elif action == "predict":
                self.agent.predict_spending()
            elif action == "summary":
                self.agent.show_summary()
            elif action == "insights":
                self.agent.show_insights()
            elif action == "help":
                self.agent.show_help()
            elif action == "exit":
                print("👋 Stopping agent...")
                await self.agent.stop()
            else:
                print("❓ Unknown command. Type 'help' for options.")

    # AGENT SETUP 
    async def setup(self):
        print("🤖 GHANA STUDENT FINANCE AGENT STARTED!")
        print("💰 Track your pocket money like a pro")
        print("📱 Commands: income, spent, balance, predict, summary, insights, help")

        self.data_file = "data.json"
        self.categories = ["food", "transport", "airtime", "data", "entertainment", "other"]
        
        self.category_insights = {
            "food": [
                "👉 Buy in bulk with roommates 👥",
                "👉 Reduce pure water sachets - carry a bottle 💧",
                "👉 Limit 'small chops' from the hawker 🍟"
            ],
            "transport": [
                "👉 Use shuttle instead of taxi when not late 🚌",
                "👉 Walk short distances to save GHS 2-3 🚶",
                "👉 Share taxi with classmates on late nights 👥"
            ],
            "airtime": [
                "👉 Buy weekly bundles instead of daily top-ups 📅",
                "👉 Check MTN/Vodafone student deals 🎓",
                "👉 Set auto-renewal to avoid emergency top-ups ⚡"
            ],
            "data": [
                "👉 Weekly bundle (GHS 10) cheaper than daily (GHS 2×7=GHS 14) 📶",
                "👉 Use campus WiFi when available 📡",
                "👉 Monitor which apps use most data 📊"
            ],
            "entertainment": [
                "👉 Limit to one 'Friday night' per week 🎉",
                "👉 Pre-game at home before going out 🏠",
                "👉 Look for student discounts at cinemas 🎬",
                "👉 Movie night with roommates > club entry 🍿"
            ],
            "other": [
                "👉 Track every cedi - small leaks sink ships 💧",
                "👉 Ask: 'Do I really need this?' 🤔",
                "👉 Wait 24 hours before non-essential purchases ⏳"
            ]
        }

        self.beliefs = {
            "balance": 0,
            "expenses": [],
            "income": []
        }

        self.load_data()
        behaviour = self.FinancialBehaviour()
        self.add_behaviour(behaviour)

    def add_income(self, user_input):
        try:
            words = user_input.split()
            amount = None
            for w in words:
                if w.isdigit():
                    amount = int(w)
                    break
            
            if amount is None:
                print("⚠️ Please specify amount: 'income 500'")
                return

            self.beliefs["balance"] += amount

            source = "unknown"
            if "from" in user_input:
                source = user_input.split("from")[1].strip()
            elif "mom" in user_input.lower() or "mother" in user_input.lower():
                source = "mom"
            elif "dad" in user_input.lower() or "father" in user_input.lower():
                source = "dad"

            self.beliefs["income"].append({
                "amount": amount,
                "source": source,
                "date": str(datetime.now())
            })

            self.save_data()
            print(f"✅ Income added: GHS {amount} from {source}")
            print(f"💰 New balance: GHS {self.beliefs['balance']}")

        except Exception as e:
            print(f"⚠️ Invalid input. Use: income 500")

    def add_expense(self, user_input):
        try:
            words = user_input.split()
            
            amount = None
            for w in words:
                if w.isdigit():
                    amount = int(w)
                    break
            
            if amount is None:
                print("⚠️ Please specify amount: 'spent 20 food'")
                return

            # Determine category
            category = "other"
            for w in words:
                if w.lower() in self.categories:
                    category = w.lower()
                    break

            # Update balance
            self.beliefs["balance"] -= amount

            # Store expense
            expense = {
                "amount": amount,
                "category": category,
                "description": user_input,
                "date": str(datetime.now())
            }
            self.beliefs["expenses"].append(expense)

            self.save_data()

            print(f"🧾 Recorded: GHS {amount} ({category})")
            print(f"💰 Balance: GHS {self.beliefs['balance']}")

            # Check for alerts
            self.check_alerts(amount, category)

        except Exception as e:
            print(f"⚠️ Use: spent 20 food")

    def check_alerts(self, amount, category):
        """Generate real-time alerts based on spending"""
        
        # Overspending alert (if expense > 1.5x average)
        if len(self.beliefs["expenses"]) >= 3:
            avg = sum(e["amount"] for e in self.beliefs["expenses"]) / len(self.beliefs["expenses"])
            if amount > avg * 1.5:
                print("⚠️ OVERSPENDING ALERT: This is higher than your usual spending!")
        
        # Low balance alert
        if self.beliefs["balance"] < 20:
            print("⚠️ LOW BALANCE: You have less than GHS 20 left!")
        
        # Category-specific real-time alerts
        if category == "food" and amount > 40:
            print("🍔 That's a lot for one meal! Bush canteen is cheaper.")
        elif category == "transport" and amount > 20:
            print("🚗 Consider shuttle next time to save GHS 10-15!")
        elif category == "airtime" and amount > 15:
            print("📱 That much airtime? Check if you need a data bundle instead.")
        elif category == "data" and amount < 5:
            print("📶 Daily bundles add up! Weekly is cheaper.")

    def predict_spending(self):
        """Predict how many days money will last"""
        if not self.beliefs["expenses"]:
            print("📊 Not enough data to predict yet. Add some expenses first.")
            return

        # Calculate average daily spend (last 7 days or all if fewer)
        recent = self.beliefs["expenses"][-7:] if len(self.beliefs["expenses"]) > 7 else self.beliefs["expenses"]
        
        if not recent:
            return
            
        # Group by day
        daily_totals = {}
        for e in recent:
            date = e["date"].split()[0]  # Just the date part
            if date not in daily_totals:
                daily_totals[date] = 0
            daily_totals[date] += e["amount"]
        
        avg_daily = sum(daily_totals.values()) / len(daily_totals) if daily_totals else 0
        
        if avg_daily > 0:
            days = int(self.beliefs["balance"] / avg_daily)
            print(f"📉 Based on your spending, your money will last ~{days} days")
            
            if days < 7:
                print("⚠️ That's less than a week! Time to cut back.")
            elif days < 14:
                print("👍 You have about 2 weeks. Spend wisely.")
            else:
                print("✅ Looking good! You're on track.")
        else:
            print("📊 Can't predict yet. Add more expenses.")

    def show_summary(self):
        """Show spending summary by category"""
        total_expense = sum(e["amount"] for e in self.beliefs["expenses"])
        total_income = sum(i["amount"] for i in self.beliefs["income"])

        print("📊 FINANCIAL SUMMARY")
        print(f"💰 Total Income:  GHS {total_income}")
        print(f"💸 Total Expenses: GHS {total_expense}")
        print(f"💵 Current Balance: GHS {self.beliefs['balance']}")
        
        if total_income > 0:
            spent_pct = (total_expense / total_income) * 100
            print(f"📈 Spent: {spent_pct:.1f}% of income")

        # Category breakdown
        if self.beliefs["expenses"]:
            print("\n📂 SPENDING BY CATEGORY:")
            category_totals = {}
            for e in self.beliefs["expenses"]:
                cat = e["category"]
                category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

            # Sort by highest spending
            sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            for cat, amt in sorted_cats:
                pct = (amt / total_expense) * 100
                bar = "█" * int(pct / 5)
                print(f"  {cat.capitalize():12} GHS {amt:6.2f} {bar} {pct:.0f}%")
            
        else:
            print("\n📭 No expenses recorded yet.")
        

    def show_insights(self):
        """Generate personalized insights based on spending patterns"""
        if not self.beliefs["expenses"]:
            print("\n💡 No insights yet. Add some expenses first.")
            return

        print("🔍 PERSONALIZED INSIGHTS")


        # Calculate category totals
        category_totals = {}
        for e in self.beliefs["expenses"]:
            cat = e["category"]
            category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

        if not category_totals:
            return

        total_expense = sum(category_totals.values())
        
        # Find highest spending category
        highest_cat = max(category_totals, key=category_totals.get)
        highest_amt = category_totals[highest_cat]
        highest_pct = (highest_amt / total_expense) * 100

        print(f"📊 Your biggest expense is {highest_cat.upper()} ({highest_pct:.0f}% of total)")

        # Category-specific insights
        if highest_cat == "food":
            print("👉 Try eating at Bush canteen for a change 🍽️")
            print("👉 Consider cooking with roommates to save money 👥")
            print("👉 Reduce pure water sachets - carry a bottle 💧")
        elif highest_cat == "airtime":
            print("👉 Buy weekly bundles instead of daily top-ups 📅")
            print("👉 Check MTN/Vodafone student deals 🎓")
        elif highest_cat == "data":
            print("👉 Weekly bundle (GHS 10) cheaper than daily (GHS 14/week) 📶")
            print("👉 Use campus WiFi more often 📡")
        elif highest_cat == "transport":
            print("👉 Use shuttle instead of taxi when not late 🚌")
            print("👉 Walk short distances to save GHS 2-3 🚶")
            print("👉 Share taxi with classmates on late nights 👥")
        elif highest_cat == "entertainment":
            print("👉 Limit to one 'Friday night' per week 🎉")
            print("👉 Pre-game at home before going out 🏠")
            print("👉 Look for student discounts at cinemas 🎬")
        else:
            # Random insight from other category
            import random
            print(random.choice(self.category_insights["other"]))

        # Additional insights based on patterns
        if len(self.beliefs["expenses"]) > 10:
            # Check for many small transactions (leakage)
            small_txns = [e for e in self.beliefs["expenses"] if e["amount"] < 10]
            if len(small_txns) > len(self.beliefs["expenses"]) * 0.3:  # 30% are small
                print("\n💧 LEAKAGE DETECTED: Many small transactions add up!")
                print("   Those GHS 2-5 'small-small' expenses become GHS 100+ monthly")

        # Check balance trend
        if self.beliefs["balance"] < 50:
            print(f"\n⚠️ CRITICAL: Balance is GHS {self.beliefs['balance']} - stretch it!")
        elif self.beliefs["balance"] < 100:
            print(f"\n⚠️ Warning: Only GHS {self.beliefs['balance']} left - spend carefully")


    def show_help(self):
        """Show available commands"""
        print("📚 AVAILABLE COMMANDS")
        print("💰 income <amount>           - Add income (e.g., 'income 500 from mom')")
        print("💸 spent <amount> <category> - Record expense with category")
        print("💵 balance                   - Check current balance")
        print("📊 summary                   - Show spending summary")
        print("📉 predict                   - Predict days money will last")
        print("🔍 insights                  - Get personalized spending insights")
        print("❓ help                       - Show this help menu")
        print("👋 exit                      - Stop the agent")
        print("\n📂 Categories: food, transport, airtime, data, entertainment, other")

    # STORAGE 

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.beliefs, f, indent=4)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.beliefs = json.load(f)
            print(f"📂 Loaded previous data. Balance: GHS {self.beliefs['balance']}")


# RUN AGENT

async def main():
    jid = "financialagent@xmpp.jp"
    password = "Kwesi316"      

    agent = FinancialAgent(jid, password)
    await agent.start()

    print("\n✅ Agent is running... Type 'help' for commands. Press Ctrl+C to stop.\n")

    try:
        while agent.is_alive():
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping agent...")
        await agent.stop()
        print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())