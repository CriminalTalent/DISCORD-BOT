# sheet_manager.py
# 구글 시트 연동 관리자

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

class SheetManager:
    def __init__(self, credentials_file, sheet_id):
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.client = None
        self.spreadsheet = None
        self._connect()
        self._ensure_sheets()
    
    def _connect(self):
        """구글 시트 연결"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            print(f"[SHEET] 연결 성공: {self.spreadsheet.title}")
            
        except Exception as e:
            print(f"[SHEET ERROR] 연결 실패: {e}")
            raise
    
    def _ensure_sheets(self):
        """필요한 시트들이 존재하는지 확인하고 없으면 생성"""
        required_sheets = {
            '사용자': ['ID', '이름', '갈레온', '아이템', '메모', '기숙사', 
                      '마지막베팅날짜', '베팅횟수', '출석날짜', '마지막타로날짜', '기숙사점수'],
            '아이템': ['아이템명', '설명', '가격', '판매여부', '사용가능여부'],
            '로그': ['타임스탬프', '사용자', '명령어', '내용']
        }
        
        existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
        
        for sheet_name, headers in required_sheets.items():
            if sheet_name not in existing_sheets:
                print(f"[SHEET] '{sheet_name}' 시트 생성 중...")
                ws = self.spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=100,
                    cols=len(headers)
                )
                ws.append_row(headers)
                print(f"[SHEET] '{sheet_name}' 시트 생성 완료")
    
    def get_worksheet(self, sheet_name):
        """시트 가져오기"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"[ERROR] '{sheet_name}' 시트를 찾을 수 없습니다.")
            return None
    
    # ============================================
    # 사용자 관리
    # ============================================
    
    def find_user(self, user_id):
        """사용자 찾기"""
        try:
            ws = self.get_worksheet('사용자')
            if not ws:
                return None
            
            records = ws.get_all_records()
            
            for idx, record in enumerate(records, start=2):
                if str(record.get('ID', '')).strip() == str(user_id).strip():
                    return {
                        'row': idx,
                        'id': record.get('ID', ''),
                        'name': record.get('이름', ''),
                        'galleons': int(record.get('갈레온', 0)),
                        'items': record.get('아이템', ''),
                        'memo': record.get('메모', ''),
                        'house': record.get('기숙사', ''),
                        'last_bet_date': record.get('마지막베팅날짜', ''),
                        'bet_count': int(record.get('베팅횟수', 0)),
                        'attendance_date': record.get('출석날짜', ''),
                        'last_tarot_date': record.get('마지막타로날짜', ''),
                        'house_score': int(record.get('기숙사점수', 0))
                    }
            
            return None
            
        except Exception as e:
            print(f"[ERROR] find_user 실패: {e}")
            return None
    
    def create_user(self, user_id, name, initial_galleons=100):
        """새 사용자 생성"""
        try:
            ws = self.get_worksheet('사용자')
            if not ws:
                return False
            
            row = [
                str(user_id),
                str(name),
                initial_galleons,
                '',
                '',
                '',
                '',
                0,
                '',
                '',
                0
            ]
            
            ws.append_row(row)
            print(f"[USER] 새 사용자 생성: {name} (ID: {user_id})")
            return True
            
        except Exception as e:
            print(f"[ERROR] create_user 실패: {e}")
            return False
    
    def update_user(self, user_id, updates):
        """사용자 정보 업데이트"""
        try:
            user = self.find_user(user_id)
            if not user:
                return False
            
            ws = self.get_worksheet('사용자')
            row = user['row']
            
            col_map = {
                'id': 1, 'name': 2, 'galleons': 3, 'items': 4,
                'memo': 5, 'house': 6, 'last_bet_date': 7,
                'bet_count': 8, 'attendance_date': 9,
                'last_tarot_date': 10, 'house_score': 11
            }
            
            for key, value in updates.items():
                if key in col_map:
                    col = col_map[key]
                    ws.update_cell(row, col, value)
            
            print(f"[USER] 업데이트 완료: {user_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] update_user 실패: {e}")
            return False
    
    # ============================================
    # 아이템 관리
    # ============================================
    
    def find_item(self, item_name):
        """아이템 정보 찾기"""
        try:
            ws = self.get_worksheet('아이템')
            if not ws:
                return None
            
            records = ws.get_all_records()
            
            for record in records:
                if record.get('아이템명', '').strip() == item_name.strip():
                    return {
                        'name': record.get('아이템명', ''),
                        'description': record.get('설명', ''),
                        'price': int(record.get('가격', 0)),
                        'sellable': str(record.get('판매여부', '')).upper() == 'TRUE',
                        'usable': str(record.get('사용가능여부', '')).upper() == 'TRUE'
                    }
            
            return None
            
        except Exception as e:
            print(f"[ERROR] find_item 실패: {e}")
            return None
    
    def get_all_items(self, sellable_only=False):
        """모든 아이템 목록 가져오기"""
        try:
            ws = self.get_worksheet('아이템')
            if not ws:
                return []
            
            records = ws.get_all_records()
            items = []
            
            for record in records:
                item = {
                    'name': record.get('아이템명', ''),
                    'description': record.get('설명', ''),
                    'price': int(record.get('가격', 0)),
                    'sellable': str(record.get('판매여부', '')).upper() == 'TRUE',
                    'usable': str(record.get('사용가능여부', '')).upper() == 'TRUE'
                }
                
                if sellable_only and not item['sellable']:
                    continue
                
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"[ERROR] get_all_items 실패: {e}")
            return []
    
    def add_item_to_user(self, user_id, item_name):
        """사용자에게 아이템 추가"""
        user = self.find_user(user_id)
        if not user:
            return False
        
        items = user['items'].split(',') if user['items'] else []
        items = [i.strip() for i in items if i.strip()]
        items.append(item_name)
        
        return self.update_user(user_id, {'items': ','.join(items)})
    
    def remove_item_from_user(self, user_id, item_name):
        """사용자에게서 아이템 제거"""
        user = self.find_user(user_id)
        if not user:
            return False
        
        items = user['items'].split(',') if user['items'] else []
        items = [i.strip() for i in items if i.strip()]
        
        if item_name in items:
            items.remove(item_name)
            return self.update_user(user_id, {'items': ','.join(items)})
        
        return False
    
    def get_user_items(self, user_id):
        """사용자 아이템 목록"""
        user = self.find_user(user_id)
        if not user:
            return {}
        
        items = user['items'].split(',') if user['items'] else []
        items = [i.strip() for i in items if i.strip()]
        
        item_counts = {}
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        return item_counts
    
    # ============================================
    # 로그
    # ============================================
    
    def log_message(self, user, command, content):
        """로그 기록"""
        try:
            ws = self.get_worksheet('로그')
            if not ws:
                return False
            
            kst = pytz.timezone('Asia/Seoul')
            timestamp = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
            
            row = [timestamp, str(user), str(command), str(content)]
            ws.append_row(row)
            
            return True
            
        except Exception as e:
            print(f"[LOG ERROR] {e}")
            return False
    
    def get_recent_logs(self, limit=10):
        """최근 로그 조회"""
        try:
            ws = self.get_worksheet('로그')
            if not ws:
                return []
            
            records = ws.get_all_records()
            recent = records[-limit:] if len(records) > limit else records
            recent.reverse()
            
            return recent
            
        except Exception as e:
            print(f"[LOG ERROR] {e}")
            return []
