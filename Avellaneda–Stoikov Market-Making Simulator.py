import math
import random as rd

import matplotlib.pyplot as plt   



# Avellaneda-Stoikov quoting model
# Given the current market state, returns our bid/ask quotes and
# the probabilities of a client order arriving.
def avellaneda_stoikov_quotes(
    mid_price,
    inventory,
    volatility,
    time_remaining,
    risk_aversion,
    k,
    arrival_rate,
    dt                       
)
    
    
    reservation_price = (
        mid_price
        - inventory * risk_aversion * volatility**2 * time_remaining
    )

   
    spread = (
        risk_aversion * volatility**2 * time_remaining
        + (2 / risk_aversion) * math.log(1 + risk_aversion / k)
    )

    bid = reservation_price - spread / 2
    ask = reservation_price + spread / 2

    # Distance of quotes from the mid price 
    delta_ask = max(0.0, ask - mid_price)    
    delta_bid = max(0.0, mid_price - bid)    

    # Order arrival intensity: lambda(delta) = A * exp(-k * delta)
    
    lambda_ask = arrival_rate * math.exp(-k * delta_ask)   
    lambda_bid = arrival_rate * math.exp(-k * delta_bid)   

   
    trade_probability = 1.0 - math.exp(-(lambda_ask + lambda_bid) * dt)

    # buy_probability = P(client buys | a fill happens)
    buy_probability = (
        lambda_ask / (lambda_ask + lambda_bid)
        if (lambda_ask + lambda_bid) > 0.0 else 0.5)

    return bid, ask, reservation_price, spread, trade_probability, buy_probability



rd.seed(42)              
steps = 1000             
dt = 1 / steps            
starting_price = 100
volatility = 0.5
current_price = starting_price

cash = 0.00
inventory = 0

market_data = []


# Main simulation loop

for step in range(steps):

   #setting the price
    price_step = rd.gauss(0, volatility * math.sqrt(dt))
    current_price += price_step

    # Get quotes from the function
    time_remaining = (steps - step) / steps

    bid, ask, reservation_price, spread, trade_probability, buy_probability = avellaneda_stoikov_quotes(
        mid_price=current_price,
        inventory=inventory,
        volatility=volatility,
        time_remaining=time_remaining,
        risk_aversion=0.1,
        k=1.5,
        arrival_rate=200.0,   
        dt=dt)            

    order_arrival = rd.random()

    order_status = 'no order'
    order_size = 0

    #3. Order execution & state update
    if order_arrival < trade_probability:

        order_size = rd.randint(1, 10)
        buy_roll = rd.random()

        if buy_roll < buy_probability:
            # Client buys from us at our ask
            order_status = 'buy'
            inventory -= 1 * order_size
            cash += ask * order_size
        else:
            # Client sells to us at our bid
            order_status = 'sell'
            inventory += 1 * order_size
            cash -= bid * order_size

    # 4. Mark-to-market accounting
    # Total PnL = realized cash + value of current holding
    total_pnl = cash + (inventory * current_price)

    
    if (step + 1) % 100 == 0:
        print(f"step {step+1}, order {order_status}, size {order_size}, "
              f"inventory {inventory}, cash {cash:8.2f}, pnl {total_pnl:8.2f}")

    market_data.append({
        "step": step + 1,
        "price": current_price,
        "bid": bid,                          
        "ask": ask,                           
        "reservation_price": reservation_price,   
        "spread": spread,                     
        "side": order_status if order_status != "no order" else None,
        "size": order_size,
        "inventory": inventory,
        "cash": cash,
        "pnl": total_pnl})



#plots
final_pnl = market_data[-1]["pnl"]
max_inventory = max(abs(d["inventory"]) for d in market_data)
num_trades = sum(1 for d in market_data if d["side"] is not None)
print(f"\nFinal PnL: {final_pnl:.2f} | Trades: {num_trades} | Max |inventory|: {max_inventory}")

steps_axis = [d["step"] for d in market_data]

fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

axes[0].plot(steps_axis, [d["price"] for d in market_data], label="mid price", color="black")
axes[0].plot(steps_axis, [d["bid"] for d in market_data], label="our bid", alpha=0.6)
axes[0].plot(steps_axis, [d["ask"] for d in market_data], label="our ask", alpha=0.6)
axes[0].set_ylabel("Price")
axes[0].legend()

axes[1].plot(steps_axis, [d["inventory"] for d in market_data], color="tab:orange")
axes[1].axhline(0, color="grey", linewidth=0.5)
axes[1].set_ylabel("Inventory")

axes[2].plot(steps_axis, [d["pnl"] for d in market_data], color="tab:green")
axes[2].set_ylabel("PnL")
axes[2].set_xlabel("Step")

plt.tight_layout()
plt.savefig("simulation_results.png", dpi=150)   # saved image goes in the README
plt.show()