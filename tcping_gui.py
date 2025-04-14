import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import time
import threading
import queue
import statistics

class TCPingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WIZnet TCPing")
        
        # 기본 창 크기 조정 및 최소 크기 설정
        self.root.geometry("550x400")
        self.root.minsize(450, 350)
        
        # 입력 프레임 - 그리드 레이아웃으로 변경
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill=tk.X)
        
        # IP 주소 입력
        ttk.Label(input_frame, text="IP Address:").pack(side=tk.LEFT, padx=5)
        self.ip_entry = ttk.Entry(input_frame, width=15)
        self.ip_entry.pack(side=tk.LEFT, padx=2)
        self.ip_entry.insert(0, "192.168.11.2")
        
        # 포트 입력
        ttk.Label(input_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(input_frame, width=8)
        self.port_entry.pack(side=tk.LEFT, padx=2)
        self.port_entry.insert(0, "5000")
        
        # Count 입력
        ttk.Label(input_frame, text="Count:").pack(side=tk.LEFT, padx=5)
        self.count_entry = ttk.Entry(input_frame, width=5)
        self.count_entry.pack(side=tk.LEFT, padx=2)
        self.count_entry.insert(0, "0")
        
        # 버튼 프레임 - 메인 프레임에 직접 추가
        self.start_button = ttk.Button(input_frame, text="Start", command=self.start_tcping, width=8)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = ttk.Button(input_frame, text="Reset", command=self.reset_fields, width=8)
        self.reset_button.pack(side=tk.LEFT, padx=2)
        
        # 결과 출력 영역 - 패딩 조정 및 확장 가능하게 설정
        result_frame = ttk.Frame(root, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 상태 변수
        self.is_running = False
        self.thread = None
        self.queue = queue.Queue()
        
        # 통계 데이터
        self.successful_pings = 0
        self.failed_pings = 0
        self.ping_times = []
        
        # 큐 체크 시작
        self.check_queue()
    
    def reset_fields(self):
        """Reset input fields and results."""
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, "192.168.11.2")
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, "5000")
        self.count_entry.delete(0, tk.END)
        self.count_entry.insert(0, "0")
        self.result_text.delete(1.0, tk.END)
        self.queue.put("Reset completed")
        
        # Reset statistics
        self.successful_pings = 0
        self.failed_pings = 0
        self.ping_times = []
    
    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.result_text.insert(tk.END, message + "\n")
                self.result_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
    
    def print_statistics(self):
        """Print statistics information."""
        total_pings = self.successful_pings + self.failed_pings
        if total_pings > 0:
            fail_rate = (self.failed_pings / total_pings) * 100
            self.queue.put("\nPing statistics for {}:{}".format(
                self.ip_entry.get(), self.port_entry.get()
            ))
            self.queue.put("     {} probes sent.".format(total_pings))
            self.queue.put("     {} successful, {} failed.  ({:.2f}% fail)".format(
                self.successful_pings, self.failed_pings, fail_rate
            ))
            
            if self.ping_times:
                min_time = min(self.ping_times)
                max_time = max(self.ping_times)
                avg_time = statistics.mean(self.ping_times)
                self.queue.put("Approximate trip times in milli-seconds:")
                self.queue.put("     Minimum = {:.3f}ms, Maximum = {:.3f}ms, Average = {:.3f}ms".format(
                    min_time, max_time, avg_time
                ))
    
    def tcping(self, host, port, count):
        self.is_running = True
        self.start_button.config(text="Stop", command=self.stop_tcping)
        
        # Reset statistics
        self.successful_pings = 0
        self.failed_pings = 0
        self.ping_times = []
        
        i = 0
        while self.is_running and (count == 0 or i < count):
            try:
                # Create TCP socket with optimized options
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)  # 타임아웃 설정 2초
                
                # 소켓 옵션 최적화 (Nagle 알고리즘 비활성화)
                try:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    # 소켓 재사용 설정
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except:
                    pass  # 일부 시스템에서는 지원하지 않을 수 있음
                
                # Record start time - 고정밀 타이머 사용
                start_time = time.perf_counter()
                
                # Try TCP connection
                result = sock.connect_ex((host, port))
                
                # Record end time
                end_time = time.perf_counter()
                elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if result == 0:
                    # Connection successful
                    self.successful_pings += 1
                    
                    # 최소값 필터링 - 정밀도 관련 설정
                    if elapsed < 0.001:  # 너무 작은 값 방지
                        elapsed = 0.001
                    
                    # 값이 비정상적으로 크면 최대값 필터링
                    if elapsed > 2000:  # 2초(2000ms) 초과 시 타임아웃으로 간주
                        elapsed = 2000
                    
                    self.ping_times.append(elapsed)
                    
                    # 커맨드라인 tcping과 동일한 형식으로 출력
                    self.queue.put(f"Probing {host}:{port}/tcp - Port is open - time={elapsed:.3f}ms")
                    
                    # 연결 성공 후 1ms 대기
                    time.sleep(0.001)
                    
                    # 명시적으로 연결 종료
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except:
                        pass  # 이미 닫힌 소켓에 대한 예외 처리
                    
                    sock.close()
                    
                    # 다음 연결 시도 전 1초 대기 (메시지 없이)
                    time.sleep(1)
                else:
                    # Connection failed
                    self.failed_pings += 1
                    error_code = socket.errno.errorcode.get(result, f"Unknown error ({result})")
                    self.queue.put(f"Probing {host}:{port}/tcp - Port is closed - {error_code}")
                    
                    # 연결 실패 시에도 소켓 정리
                    sock.close()
                    
                    # 다음 연결 시도 전 1초 대기 (메시지 없이)
                    time.sleep(1)
                
                i += 1
                
            except socket.timeout:
                self.failed_pings += 1
                self.queue.put(f"Probing {host}:{port}/tcp - Timeout")
                # 소켓 정리
                try:
                    sock.close()
                except:
                    pass
                # 다음 연결 시도 전 1초 대기 (메시지 없이)
                time.sleep(1)
            except socket.error as e:
                self.failed_pings += 1
                self.queue.put(f"Error: {e}")
                # 소켓 정리
                try:
                    sock.close()
                except:
                    pass
                # 다음 연결 시도 전 1초 대기 (메시지 없이)
                time.sleep(1)
        
        # Print statistics when test ends
        self.print_statistics()
        
        self.is_running = False
        self.start_button.config(text="Start", command=self.start_tcping)
    
    def start_tcping(self):
        try:
            host = self.ip_entry.get()
            port = int(self.port_entry.get())
            count = int(self.count_entry.get())
            
            self.thread = threading.Thread(
                target=self.tcping,
                args=(host, port, count)
            )
            self.thread.daemon = True
            self.thread.start()
            
        except ValueError:
            self.queue.put("Please enter valid IP address, port, and count.")
    
    def stop_tcping(self):
        self.is_running = False

def main():
    root = tk.Tk()
    app = TCPingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 