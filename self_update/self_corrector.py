"""
自我修正與更新系統
根據錯誤日誌自動調整配置和腳本
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime

class SelfCorrector:
    """自我修正器"""
    
    def __init__(self, config_dir="~/.openclaw/ai-operator/config"):
        self.config_dir = Path(os.path.expanduser(config_dir))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.error_log = self.config_dir / "error_history.json"
        self.corrections = []
        
    def analyze_errors(self, logs):
        """分析錯誤模式"""
        error_patterns = {
            "timeout": [],
            "element_not_found": [],
            "permission_denied": [],
            "network_error": []
        }
        
        for log in logs:
            if log.get("status") == "failure":
                details = log.get("details", {})
                error_msg = details.get("error", "")
                
                if "timeout" in error_msg.lower():
                    error_patterns["timeout"].append(log)
                elif "not found" in error_msg.lower() or "找不到" in error_msg:
                    error_patterns["element_not_found"].append(log)
                elif "permission" in error_msg.lower():
                    error_patterns["permission_denied"].append(log)
                elif "network" in error_msg.lower() or "連線" in error_msg:
                    error_patterns["network_error"].append(log)
                    
        return error_patterns
    
    def generate_corrections(self, error_patterns):
        """生成修正方案"""
        corrections = []
        
        # Timeout 錯誤
        if len(error_patterns["timeout"]) > 3:
            corrections.append({
                "type": "timeout_adjustment",
                "description": "增加逾時時間",
                "action": "increase_timeout",
                "params": {"timeout_ms": 5000}
            })
            
        # Element not found 錯誤
        if len(error_patterns["element_not_found"]) > 2:
            corrections.append({
                "type": "selector_optimization",
                "description": "優化元素選擇器",
                "action": "update_selectors",
                "params": {"use_flexible_selector": True}
            })
            
        # 權限錯誤
        if len(error_patterns["permission_denied"]) > 0:
            corrections.append({
                "type": "permission_fix",
                "description": "修復權限問題",
                "action": "check_permissions",
                "params": {}
            })
            
        return corrections
    
    def apply_correction(self, correction):
        """應用修正"""
        result = {
            "correction": correction,
            "timestamp": datetime.now().isoformat(),
            "status": "applied"
        }
        
        try:
            if correction["type"] == "timeout_adjustment":
                # 更新逾時配置
                self.update_timeout_config(correction["params"])
                
            elif correction["type"] == "selector_optimization":
                # 更新選擇器配置
                self.update_selector_config(correction["params"])
                
            elif correction["type"] == "permission_fix":
                # 執行權限檢查
                self.fix_permissions()
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        self.corrections.append(result)
        return result
    
    def update_timeout_config(self, params):
        """更新逾時配置"""
        config_file = self.config_dir / "timeouts.json"
        config = {}
        
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                
        config.update(params)
        config["last_updated"] = datetime.now().isoformat()
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
            
    def update_selector_config(self, params):
        """更新選擇器配置"""
        config_file = self.config_dir / "selectors.json"
        config = {}
        
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                
        config.update(params)
        config["last_updated"] = datetime.now().isoformat()
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
            
    def fix_permissions(self):
        """修復權限"""
        # 檢查並修復目錄權限
        import subprocess
        
        dirs_to_check = [
            "~/.openclaw/ai-operator/logs",
            "~/.openclaw/ai-operator/data",
            "~/.openclaw/browser"
        ]
        
        for dir_path in dirs_to_check:
            expanded = os.path.expanduser(dir_path)
            subprocess.run(["chmod", "755", expanded], check=False)


class AutoUpdateManager:
    """自動更新管理器"""
    
    def __init__(self, version_file="~/.openclaw/ai-operator/VERSION"):
        self.version_file = Path(os.path.expanduser(version_file))
        self.current_version = "1.0.0"
        
        if self.version_file.exists():
            self.current_version = self.version_file.read_text().strip()
            
    def get_current_version(self):
        """取得當前版本"""
        return self.current_version
    
    def bump_version(self):
        """遞增版本"""
        parts = self.current_version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        self.current_version = ".".join(parts)
        
        self.version_file.write_text(self.current_version)
        return self.current_version
    
    def create_backup(self):
        """創建備份"""
        import shutil
        from datetime import datetime
        
        backup_dir = Path("~/.openclaw/ai-operator/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        
        # 備份關鍵配置
        shutil.copytree(
            os.path.expanduser("~/.openclaw/ai-operator/config"),
            backup_path / "config",
            dirs_exist_ok=True
        )
        
        return str(backup_path)


class HealthChecker:
    """健康檢查"""
    
    def __init__(self):
        self.checks = []
        
    def run_checks(self):
        """執行檢查"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # 檢查 1: 目錄權限
        results["checks"].append(self.check_directory_permissions())
        
        # 檢查 2: 磁碟空間
        results["checks"].append(self.check_disk_space())
        
        # 檢查 3: 瀏覽器可用性
        results["checks"].append(self.check_browser_available())
        
        # 檢查 4: 日誌健康
        results["checks"].append(self.check_log_health())
        
        results["overall_health"] = self.calculate_health_score(results["checks"])
        
        return results
        
    def check_directory_permissions(self):
        """檢查目錄權限"""
        import os
        
        dirs = [
            "~/.openclaw/ai-operator/logs",
            "~/.openclaw/ai-operator/data",
            "~/.openclaw/browser"
        ]
        
        all_ok = True
        for dir_path in dirs:
            expanded = os.path.expanduser(dir_path)
            if os.path.exists(expanded):
                if not os.access(expanded, os.W_OK):
                    all_ok = False
                    
        return {
            "name": "directory_permissions",
            "status": "ok" if all_ok else "warning",
            "message": "所有目錄權限正常" if all_ok else "部分目錄無法寫入"
        }
        
    def check_disk_space(self):
        """檢查磁碟空間"""
        import shutil
        
        stat = shutil.disk_usage("/")
        free_gb = stat.free / (1024**3)
        
        return {
            "name": "disk_space",
            "status": "ok" if free_gb > 1 else "warning",
            "message": f"可用空間: {free_gb:.1f} GB"
        }
        
    def check_browser_available(self):
        """檢查瀏覽器"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["which", "google-chrome-stable"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    "name": "browser",
                    "status": "ok",
                    "message": "Chrome 可用"
                }
        except:
            pass
            
        return {
            "name": "browser",
            "status": "warning",
            "message": "Chrome 未安裝"
        }
        
    def check_log_health(self):
        """檢查日誌健康"""
        import os
        
        log_dir = os.path.expanduser("~/.openclaw/ai-operator/logs")
        if not os.path.exists(log_dir):
            return {
                "name": "log_health",
                "status": "ok",
                "message": "日誌目錄正常"
            }
            
        # 檢查日誌大小
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, f))
            for dirpath, _, files in os.walk(log_dir)
            for f in files
        )
        
        size_mb = total_size / (1024 * 1024)
        
        return {
            "name": "log_health",
            "status": "ok" if size_mb < 100 else "warning",
            "message": f"日誌大小: {size_mb:.1f} MB"
        }
        
    def calculate_health_score(self, checks):
        """計算健康分數"""
        ok_count = sum(1 for c in checks if c["status"] == "ok")
        total = len(checks)
        
        return round(ok_count / total * 100, 1)


# 全域實例
corrector = SelfCorrector()
update_manager = AutoUpdateManager()
health_checker = HealthChecker()
