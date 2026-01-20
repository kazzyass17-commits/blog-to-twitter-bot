from time import sleep
from datetime import datetime
from post_both_accounts import main

for i in range(3):
    print("="*60)
    print(f"閾ｨ譎よ兜遞ｿ {i+1}/3 髢句ｧ・ {datetime.now()}")
    print("="*60)
    main()
    if i < 2:
        print("谺｡縺ｮ謚慕ｨｿ縺ｾ縺ｧ10蛻・ｾ・ｩ溘＠縺ｾ縺・..")
        sleep(600)
