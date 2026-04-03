import heapq
import random
import time
import subprocess
import sys

# ==========================================
# 劇情開場 
# ==========================================
def show_prologue():
    print("\n" + "="*50)
    slow_print("深夜，起始之村的郊外...", 0.1)
    time.sleep(1)
    slow_print("當你從火堆旁驚醒時，發現身邊空空如也。", 0.08)
    slow_print("你的聖劍、盾牌，甚至是備用的藥水，都被那群該死的強盜洗劫一空了。", 0.08)
    slow_print("他們嘲笑著往北方逃竄，那裡是兇險的『強盜城寨』。", 0.08)
    print("-" * 30)
    slow_print("你咬緊牙關，雖然失去了武器，但你的大腦還在。", 0.08)
    slow_print("利用你腦中的「路徑規劃演算法」，避開致命危險，奪回屬於你的一切！", 0.08)
    print("="*50 + "\n")
    time.sleep(1.5)

def slow_print(text, speed=0.08):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

# ==========================================
# 動態地圖生成 
# ==========================================
def generate_world():
    locations = ["起始之村", "迷霧森林", "幽靜小徑", "荒廢礦坑", "死亡泥沼", 
                 "古老廢墟", "陰森峽谷", "迴聲山洞", "惡魔平原", "強盜城寨"]
    
    dynamic_map = {loc: [] for loc in locations}
    
    for i in range(len(locations)-1):
        danger = random.randint(15, 30)
        dynamic_map[locations[i]].append((locations[i+1], danger))
        dynamic_map[locations[i+1]].append((locations[i], danger))
    
    extra_lanes = 0
    while extra_lanes < 7:
        loc1, loc2 = random.sample(locations, 2)
        
        is_direct_shortcut = (loc1 == "起始之村" and loc2 == "強盜城寨") or \
                             (loc2 == "起始之村" and loc1 == "強盜城寨")
        
        already_connected = loc2 in [d for d, _ in dynamic_map[loc1]]
        
        if not is_direct_shortcut and not already_connected and loc1 != loc2:
            danger = random.randint(10, 70) 
            dynamic_map[loc1].append((loc2, danger))
            dynamic_map[loc2].append((loc1, danger))
            extra_lanes += 1
            
    return dynamic_map

# ==========================================
# Dijkstra 
# ==========================================
def dijkstra_navigation(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    prev = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        if curr_node == end: break
        if curr_dist > distances[curr_node]: continue
        for neighbor, weight in graph.get(curr_node, []):
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev[neighbor] = curr_node
                heapq.heappush(pq, (new_dist, neighbor))
    
    path = []
    temp = end
    while temp is not None:
        path.append(temp)
        temp = prev[temp]
    path.reverse()
    return distances[end], path

# ==========================================
# 遊戲主程式 
# ==========================================
def main():
    show_prologue()
    
    print("="*50)
    print("   【半夜被強盜偷走裝備的我: 踏上最優路徑的復仇是否搞錯了什麼?】")
    print("="*50)
    
    world_map = generate_world()
    player = {
        "location": "起始之村",
        "hp": 100,
        "max_hp": 100,
        "potions": 2
    }
    
    print("系統：世界地圖已動態生成。權重（傷害值）已存入資料庫。")
    print("提示：你的目標是抵達『強盜城寨』。")

    while True:
        hp_percent = max(0, player['hp']) // 10
        hp_bar = "█" * hp_percent + "░" * (10 - hp_percent)
        
        print(f"\n--- 當前狀態 ---")
        print(f"📍 位置: {player['location']}")
        print(f"❤️ 血量: [{hp_bar}] {player['hp']}/{player['max_hp']}")
        print(f"🧪 藥水: {player['potions']} 瓶")
        print("-" * 20)
        print("指令：[1] 移動 [2] 喝藥水 [3] 導航作弊系統 [4] 查看地圖資料表 [0] 離開遊戲")
        
        choice = input("請輸入編號: ")

        if choice == "1":
            options = world_map[player['location']]
            print("\n可前往的地區：")
            for i, (dest, danger) in enumerate(options):
                print(f" {i+1}. {dest} (預估傷害: {danger})")
            
            try:
                move_idx = int(input("你的選擇: ")) - 1
                dest, danger = options[move_idx]
                
                print(f"\n>> 前往 {dest} 的途中被怪物襲擊了！")
                time.sleep(0.5)
                print(f">> 你受到了 {danger} 點傷害。")
                
                player['hp'] -= danger
                player['location'] = dest
                
                if player['location'] == "強盜城寨":
                    print("\n" + "⚔️ " * 15)
                    slow_print("抵達了強盜城寨！你在門口的木箱中意外發現了...", 0.1)
                    slow_print("你的聖劍、盾牌，以及還沒被喝完的藥水！", 0.1)
                    slow_print("裝備就緒，準備好對強盜進行徹底的報仇了嗎...", 0.1)
                    time.sleep(1)
                    
                    try:
                        result = subprocess.run([sys.executable, "battle.py"])
                        print("\n" + "="*40)
                        if result.returncode == 0:
                            print("【終端機回報】恭喜你！奪回了尊嚴，成功的擊敗了強盜！")
                        else:
                            print("【終端機回報】你倒下了... 沒裝備被虐，有裝備還輸，真是可憐:)")
                        print("="*40)
                    except Exception as e:
                        print(f"啟動戰鬥視窗失敗，錯誤原因: {e}")
                        
                    print("冒險在此告一段落。")
                    break

                if player['hp'] <= 0:
                    print("\n☠️ 你的 HP 歸零了。即使有作弊器，沒裝備的冒險依然充滿殘酷...")
                    break
            except:
                print("⚠️ 輸入錯誤，請選擇有效的編號。")

        elif choice == "2":
            if player['potions'] > 0:
                heal = 30
                player['hp'] = min(player['max_hp'], player['hp'] + heal)
                player['potions'] -= 1
                print(f"\n🧪 喝下藥水，HP 恢復了 {heal} 點！")
            else:
                print("\n❌ 藥水已經用完了！")

        elif choice == "3":
            target = "強盜城寨"
            print(f"\n🔍 啟動 作弊系統計算至『{target}』的最優路徑...")
            time.sleep(1)
            total_damage, best_path = dijkstra_navigation(world_map, player['location'], target)
            
            if total_damage == float('inf'):
                print("❌ 警告：目前沒有任何路徑可以抵達目的地！")
            else:
                print(f"✅ 計算完成！")
                print(f"建議路線：{' -> '.join(best_path)}")
                print(f"路線風險總值：{total_damage} 點")
                
                if total_damage >= player['hp']:
                    print("⚠️ 演算法警告：以你目前的血量，走這條路『必死無疑』！建議先使用藥水。")
                else:
                    print("👍 演算法評估：目前的血量足夠支撐到抵達目的地。")

        elif choice == "4":
            print("\n--- 世界圖結構 (Graph Adjacency List) ---")
            for start, edges in world_map.items():
                print(f"[{start}] 連結至: {edges}")

        elif choice == "0":
            print("遊戲結束，謝謝參與！")
            break
        else:
            print("無效輸入。")

if __name__ == "__main__":
    main()
