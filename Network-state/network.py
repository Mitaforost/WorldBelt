import socket
import subprocess
import platform
import time
import psutil
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

class NetworkMonitor:
    def __init__(self):
        self.traffic_data = {}
        self.start_time = datetime.now()
    
    def scan_network(self, base_ip):
        """Сканируем сеть с помощью ping и ARP"""
        devices = []
        
        print(f"Сканирование сети {base_ip}1-254...")
        
        for i in range(1, 255):
            ip = f"{base_ip}{i}"
            try:
                # Проверяем доступность хоста
                if platform.system() == "Windows":
                    response = subprocess.call(['ping', '-n', '1', '-w', '100', ip], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    response = subprocess.call(['ping', '-c', '1', '-W', '1', ip], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if response == 0:
                    device_info = self.get_device_info(ip)
                    devices.append(device_info)
                    print(f"Найден: {ip} - {device_info['hostname']} - {device_info['mac']}")
                    
                    # Инициализируем сбор статистики для устройства
                    if ip not in self.traffic_data:
                        self.traffic_data[ip] = {
                            'total_upload': 0,
                            'total_download': 0,
                            'timestamps': [],
                            'upload_speeds': [],
                            'download_speeds': []
                        }
            except:
                continue
        
        return devices
    
    def get_device_info(self, ip):
        """Получаем информацию об устройстве"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            hostname = "Неизвестно"
        
        mac = "Неизвестно"
        try:
            if platform.system() == "Windows":
                result = subprocess.check_output(['arp', '-a', ip], shell=True).decode('cp866')
                lines = result.split('\n')
                for line in lines:
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[1]
            else:
                result = subprocess.check_output(['arp', '-n', ip]).decode()
                parts = result.split()
                if len(parts) >= 3:
                    mac = parts[2]
        except:
            pass
        
        # Получаем информацию о производителе по MAC
        vendor = self.get_mac_vendor(mac)
        
        return {
            'ip': ip,
            'hostname': hostname,
            'mac': mac,
            'vendor': vendor,
            'first_seen': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_mac_vendor(self, mac):
        """Определяем производителя по MAC (первые 3 байта)"""
        if mac == "Неизвестно":
            return "Неизвестно"
        
        # Здесь можно добавить базу OUI или использовать API
        return "Определить по OUI"
    
    def monitor_traffic(self, interval=10, duration=60):
        """Мониторим трафик в сети"""
        print(f"\nНачинаем мониторинг трафика на {duration} секунд...")
        
        end_time = time.time() + duration
        while time.time() < end_time:
            # Получаем статистику по сети
            net_io = psutil.net_io_counters(pernic=True)
            
            for ip, data in self.traffic_data.items():
                try:
                    # Для Windows используем netstat
                    if platform.system() == "Windows":
                        result = subprocess.check_output(['netstat', '-e'], shell=True).decode('cp866')
                        lines = result.split('\n')
                        if len(lines) >= 4:
                            parts = lines[4].split()
                            bytes_sent = int(parts[1])
                            bytes_recv = int(parts[2])
                    else:
                        # Для Linux
                        bytes_sent = net_io['eth0'].bytes_sent
                        bytes_recv = net_io['eth0'].bytes_recv
                    
                    # Рассчитываем скорость
                    current_time = datetime.now()
                    if data['timestamps']:
                        time_diff = (current_time - data['timestamps'][-1]).total_seconds()
                        upload_diff = bytes_sent - data['total_upload']
                        download_diff = bytes_recv - data['total_download']
                        
                        upload_speed = upload_diff / time_diff / 1024  # KB/s
                        download_speed = download_diff / time_diff / 1024  # KB/s
                        
                        data['upload_speeds'].append(upload_speed)
                        data['download_speeds'].append(download_speed)
                    
                    # Обновляем данные
                    data['total_upload'] = bytes_sent
                    data['total_download'] = bytes_recv
                    data['timestamps'].append(current_time)
                    
                except Exception as e:
                    print(f"Ошибка при мониторинге {ip}: {e}")
            
            time.sleep(interval)
        
        print("Мониторинг завершен")
    
    def display_traffic_stats(self):
        """Выводим статистику по трафику"""
        print("\nСтатистика использования трафика:")
        print("="*90)
        print(f"{'IP':<15} | {'Хост':<20} | {'Всего отдано (МБ)':>15} | {'Всего получено (МБ)':>15} | {'Макс. скорость отдачи (КБ/с)':>25} | {'Макс. скорость загрузки (КБ/с)':>25}")
        print("-"*90)
        
        for ip, data in self.traffic_data.items():
            total_upload_mb = data['total_upload'] / (1024 * 1024)
            total_download_mb = data['total_download'] / (1024 * 1024)
            
            max_upload = max(data['upload_speeds']) if data['upload_speeds'] else 0
            max_download = max(data['download_speeds']) if data['download_speeds'] else 0
            
            print(f"{ip:<15} | {socket.getfqdn(ip):<20} | {total_upload_mb:>15.2f} | {total_download_mb:>15.2f} | {max_upload:>25.2f} | {max_download:>25.2f}")
        
        print("="*90)
    
    def plot_traffic(self, ip):
        """Строим график трафика для конкретного IP"""
        if ip not in self.traffic_data:
            print(f"Нет данных для IP {ip}")
            return
        
        data = self.traffic_data[ip]
        if not data['timestamps']:
            print(f"Нет данных для построения графика {ip}")
            return
        
        # Создаем DataFrame для удобства
        df = pd.DataFrame({
            'time': data['timestamps'],
            'upload': data['upload_speeds'],
            'download': data['download_speeds']
        })
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['time'], df['upload'], label='Отдача (КБ/с)')
        plt.plot(df['time'], df['download'], label='Загрузка (КБ/с)')
        plt.title(f"Использование трафика для {ip}")
        plt.xlabel("Время")
        plt.ylabel("Скорость (КБ/с)")
        plt.legend()
        plt.grid()
        plt.show()
    
    def save_to_csv(self, filename="network_report.csv"):
        """Сохраняем отчет в CSV"""
        report_data = []
        
        for ip, data in self.traffic_data.items():
            total_upload_mb = data['total_upload'] / (1024 * 1024)
            total_download_mb = data['total_download'] / (1024 * 1024)
            avg_upload = sum(data['upload_speeds']) / len(data['upload_speeds']) if data['upload_speeds'] else 0
            avg_download = sum(data['download_speeds']) / len(data['download_speeds']) if data['download_speeds'] else 0
            
            report_data.append({
                'IP': ip,
                'Hostname': socket.getfqdn(ip),
                'Total Upload (MB)': round(total_upload_mb, 2),
                'Total Download (MB)': round(total_download_mb, 2),
                'Avg Upload (KB/s)': round(avg_upload, 2),
                'Avg Download (KB/s)': round(avg_download, 2),
                'Max Upload (KB/s)': round(max(data['upload_speeds']) if data['upload_speeds'] else 0, 2),
                'Max Download (KB/s)': round(max(data['download_speeds']) if data['download_speeds'] else 0, 2)
            })
        
        df = pd.DataFrame(report_data)
        df.to_csv(filename, index=False)
        print(f"Отчет сохранен в {filename}")

def main():
    print("Улучшенный сетевой монитор")
    
    # Получаем локальный IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    base_ip = ".".join(local_ip.split('.')[:3]) + "."
    
    # Инициализируем монитор
    monitor = NetworkMonitor()
    
    # Сканируем сеть
    devices = monitor.scan_network(base_ip)
    
    if not devices:
        print("Устройства не найдены")
        return
    
    # Мониторим трафик в течение 1 минуты
    monitor.monitor_traffic(duration=60)
    
    # Выводим статистику
    monitor.display_traffic_stats()
    
    # Сохраняем отчет
    monitor.save_to_csv()
    
    # Показываем график для первого устройства
    if devices:
        monitor.plot_traffic(devices[0]['ip'])

if __name__ == "__main__":
    # Убедитесь, что запускаете с правами администратора
    try:
        main()
    except PermissionError:
        print("Ошибка: Запустите скрипт с правами администратора/root")
    except Exception as e:
        print(f"Произошла ошибка: {e}")