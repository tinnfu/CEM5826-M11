from machine import UART, Pin, PWM
import time
import re
import asyncio

class Buzzer:
    # 定义音调频率
    TONES = {
        '1-': 262,
        '2-': 294,
        '3-': 330,
        '4-': 349,
        '5-': 392,
        '6-': 440,
        '7-': 494,
        '1=': 523,
        '2=': 587,
        '3=': 659,
        '4=': 698,
        '5=': 784,
        '6=': 880,
        '7=': 988,
        '1+': 1046,
        '2+': 1175,
        '3+': 1318,
        '4+': 1397,
        '5+': 1568,
        '6+': 1760,
        '7+': 1976,
        '__': 0
    }

    def __init__(self, pin = 6):
        self.buzzer = PWM(Pin(pin, Pin.OUT), freq=1000, duty=0)

    def __del__(self):
        self.buzzer.deinit()

    async def play(self, melody, duty = 10):
        i = 0
        keep = False
        while i  < len(melody):
            if melody[i] == '(':
                i += 1
                keep = True
                continue
            elif melody[i] == ')':
                i += 1
                keep = False

                # 连音结束后稍微停顿下
                self.buzzer.duty(0)
                await asyncio.sleep(0.05)
                continue

            tone, level = melody[i], melody[i+1]
            i += 2
            freq = Buzzer.TONES[tone+level]
            if freq:
                self.buzzer.init(duty=duty, freq=freq)
            else:
                self.buzzer.duty(0)  # 空拍时静音

            # 停顿一下 （四四拍每秒两个音，每个音节中间稍微停顿一下）
            await asyncio.sleep(0.2)
            if not keep:
                self.buzzer.duty(0)  # 设备占空比为0，即不上电
            await asyncio.sleep(0.05)

class Bye:
    def __init__(self, buzzer):
        self.buzzer = buzzer
    
    async def Song(self):
        # 《路在何方》
        melody = \
        "(6-1=1=6-)(3=3=3=)2=(2=1=1=1=1=1=1=1=)(7-6-6-7-)(2=2=2=)3=(1=6-6-6-6-6-6-6-)" \
        "(3=3=3=3=)(6=6=6=3=)(6=6=5=4=)(3=3=3=3=)(1=1=1=)2=(3=3=4=3=)(2=2=2=2=2=2=2=2=)" \
        "(6-6-)(3=3=)(2=3=6-6-)(1=1=1=1=1=1=3=3=)(2=7-7-3=)(2=6-1=2=)(3=3=3=3=3=3=3=3=)" \
        "(3=3=3=3=)(6=6=6=3=)(6=6=5=4=)(3=3=3=3=)(5=2=2=4=)(3=2=1=1=)(2=2=2=2=2=2=3=3=)" \
        "(2=7-7-3=)(7-6-5-5-)(6-6-6-6-6-6-)(3=3=)(5=5=5=5=5=5=)(3=5=)(6=6=6=)1+(7=6=)(5=5=)" \
        "(6=6=6=6=6=6=6=6=)(1+1+1+1+)(7=7=7=)6-(5=6=)(5=5=5=5=)(5=6=)(3=3=3=3=3=3=3=3=)" \
        "(1+1+1+1+)(7=7=7=)6=(5=6=)(5=5=5=5=)(5=6=)(3=3=3=3=3=3=3=3=)(5-6-)1=(3=3=3=)1=" \
        "(2=3=)(2=2=2=2=2=2=)(2=7-7-)3=(7-6-5-5-)(6-6-6-6-6-6-6-6-)(5-6-6-)1=(3=3=3=)1=" \
        "(2=3=)(2=2=2=2=2=2=)(3=3=5=5=5=5=)(3=3=)(7=7=7=1+7=6=5=5=)(6=6=6=6=6=6=6=6=6=6=6=6=6=6=6=6=)" \
        "(3=3=5=5=5=5=)(3=3=)(7=7=7=1+7=6=5=5=)(6=6=6=6=6=6=6=6=6=6=6=6=6=6=6=6=)"

        await self.buzzer.play(melody)

class Welcome:
    def __init__(self, buzzer):
        self.buzzer = buzzer

    async def Song(self):
        # 《小星星》
        melody = "1=1=5=5=6=6=5=__4=4=3=3=2=2=1=__5=5=4=4=3=3=2=__5=5=4=4=3=3=2=__1=1=5=5=6=6=5=__4=4=3=3=2=2=1="
        await self.buzzer.play(melody)

class Warning:
    def __init__(self, buzzer):
        self.buzzer = buzzer

    async def Song(self):
        melody = "(7=7=)(5=5=)(7=7=)(5=5=)(7=7=)(5=5=)(7=7=)(5=5=)"
        await self.buzzer.play(melody)

class Led:
    def __init__(self, r = 2, g = 3, b = 10):
        self.r_led = Pin(r, Pin.OUT)
        self.g_led = Pin(g, Pin.OUT)
        self.b_led = Pin(b, Pin.OUT)
        self._flash_done = False

    def off(self, excludes = []):
        if 'r' not in excludes:
            self.r_led.off()
        if 'g' not in excludes:
            self.g_led.off()
        if 'b' not in excludes:
            self.b_led.off()

    def on(self, signal):
        if 'r' == signal:
            self.r_led.on()
        elif 'g' == signal:
            self.g_led.on()
        elif 'b' == signal:
            self.b_led.on()

    async def flash_begin(self, signal = ['r', 'g', 'b']):
        self._flash_done = False
        self.off()
        while not self._flash_done:
            if 'r' in signal:
                self.on('r')
                await asyncio.sleep(0.2)
            self.off()
            if 'g' in signal:
                self.on('g')
                await asyncio.sleep(0.2)
            self.off()
            if 'b' in signal:
                self.on('b')
                await asyncio.sleep(0.2)
            self.off()
            await asyncio.sleep(0.2)

    def flash_end(self):
        self._flash_done = True

class Monitor:
    def __init__(self, buzzer, led):
        self.buzzer = buzzer
        self.led = led
        self.incoming = False
        self.agitation_begin = 0 
        self.idle_begin = 0
        self.last_warning = 0
        self.no_signal_begin = 0

    async def bye(self):
        self.led.off()
        if self.incoming:
            # 闪红灯+一首歌欢送
            led = asyncio.create_task(self.led.flash_begin(['r']))
            await asyncio.create_task(Bye(self.buzzer).Song())
            self.led.flash_end()
            await led
        self.incoming = False

        # 清理所有状态，等下个状态机
        self.agitation_begin = 0 
        self.idle_begin = 0
        self.last_warning = 0
        self.no_signal_end = 0

    async def welcome(self):
        self.incoming = True
        # 第一次来人，用酷炫的灯光+唱首歌欢迎
        led = asyncio.create_task(self.led.flash_begin(['r', 'g', 'b']))
        await asyncio.create_task(Welcome(self.buzzer).Song())
        self.led.flash_end()
        await led

    async def warning(self):
        led = asyncio.create_task(self.led.flash_begin(['r', 'g', 'b']))
        await asyncio.create_task(Warning(self.buzzer).Song())
        self.led.flash_end()
        await led
        self.last_warning = time.time()

    async def process(self, info):
        if not info:
            if self.no_signal_begin == 0:
                self.no_signal_begin = time.time()
            # 去噪
            if time.time() - self.no_signal_begin > 5:
                await self.bye()
            self.led.off()
            return

        self.no_signal_begin = 0

        try:
            lines = info.decode().split('\n')
        except Exception as e:
            print(e)
            self.led.off()
            return

        # v=-0.8 km/h, str=1083
        signal = 0
        count = 0
        for line in lines:
            if not line.strip():
                continue

            print(line)
            ret = re.search('str=(\d+)', line)
            if not ret:
                continue

            signal += int(ret.group(1))
            count += 1

        if count == 0:
            self.led.off()
            return
        signal /= count

        if signal < 700:
            self.agitation_begin = 0
            if self.idle_begin == 0:
                self.idle_begin = time.time()
            if time.time() - self.idle_begin > 5:
                await self.bye()
            self.led.off()
            return

        if not self.incoming:
            await self.welcome()

        self.idle_begin = 0

        if signal < 1000:
            self.agitation_begin = 0
            self.led.off()
            return

        if signal < 2000:
            self.led.off(['b'])
            self.led.on('b')
        elif signal < 3000:
            self.led.off(['g'])
            self.led.on('g')
        else:
            self.led.off(['r'])
            self.led.on('r')

        if self.agitation_begin == 0:
            self.agitation_begin = time.time()
        # 检测到持续3s的大幅动作并且距上次报警超过5s，提示安静下来
        if (time.time() - self.agitation_begin > 3) and (time.time() - self.last_warning > 5):
            await self.warning()

async def main():
    uart = UART(1, rx=1, tx=0)
    buzzer = Buzzer()
    led = Led()
    monitor = Monitor(buzzer, led)

    while 1:
        info = uart.read()
        await monitor.process(info)
        await asyncio.sleep(1)

time.sleep(5)
asyncio.run(main())