# sheet_manager.py
# 구글 시트 연동 관리자

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

class SheetManager:
    def __init__(self, credentials_file, sheet_id):
        """
        구글 시트 매니저 초기화
        
        Args:
            credentials_file: 서비스 계정 JSON 파일 경로
            sheet_id: 구글 시트 ID
        """
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.client = None
        self.spreadsheet = None
        self._connect()
    
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
    
    def get_worksheet(self, sheet_name):
        """
        특정 시트 가져오기 (없으면 생성)
        
        Args:
            sheet_name: 시트 이름
        
        Returns:
            worksheet 객체
        """
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"[SHEET] '{sheet_name}' 시트 생성")
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=100,
                cols=10
            )
            # 헤더 추가
            worksheet.append_row(['타임스탬프', '사용자', '명령어', '내용'])
        
        return worksheet
    
    def log_message(self, user, command, content):
        """
        메시지 로그 기록
        
        Args:
            user: 사용자명 (Discord username)
            command: 명령어
            content: 내용
        """
        try:
            worksheet = self.get_worksheet('로그')
            
            # 한국 시간
            kst = pytz.timezone('Asia/Seoul')
            timestamp = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
            
            row = [timestamp, str(user), str(command), str(content)]
            worksheet.append_row(row)
            
            print(f"[LOG] 저장 완료: {user} - {command}")
            return True
            
        except Exception as e:
            print(f"[LOG ERROR] 저장 실패: {e}")
            return False
    
    def get_recent_logs(self, limit=10):
        """
        최근 로그 가져오기
        
        Args:
            limit: 가져올 로그 개수
        
        Returns:
            로그 리스트 (딕셔너리 형태)
        """
        try:
            worksheet = self.get_worksheet('로그')
            all_records = worksheet.get_all_records()
            
            # 최근 N개만 (역순)
            recent = all_records[-limit:] if len(all_records) > limit else all_records
            recent.reverse()
            
            return recent
            
        except Exception as e:
            print(f"[LOG ERROR] 조회 실패: {e}")
            return []
    
    def search_logs(self, keyword):
        """
        키워드로 로그 검색
        
        Args:
            keyword: 검색 키워드
        
        Returns:
            검색 결과 리스트
        """
        try:
            worksheet = self.get_worksheet('로그')
            all_records = worksheet.get_all_records()
            
            # 키워드가 포함된 로그만 필터링
            results = [
                record for record in all_records
                if keyword.lower() in str(record.get('내용', '')).lower()
                or keyword.lower() in str(record.get('명령어', '')).lower()
            ]
            
            return results
            
        except Exception as e:
            print(f"[SEARCH ERROR] 검색 실패: {e}")
            return []
    
    def clear_logs(self):
        """로그 시트 초기화 (헤더 제외)"""
        try:
            worksheet = self.get_worksheet('로그')
            worksheet.clear()
            worksheet.append_row(['타임스탬프', '사용자', '명령어', '내용'])
            print("[LOG] 로그 초기화 완료")
            return True
            
        except Exception as e:
            print(f"[CLEAR ERROR] 초기화 실패: {e}")
            return False
