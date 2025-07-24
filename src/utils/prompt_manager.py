"""
Prompt 管理模組
處理不同類型的 AI 提示詞管理
"""
import os
from pathlib import Path
from typing import List, Dict


class PromptManager:
    """Prompt 管理器"""
    
    def __init__(self):
        """初始化 Prompt 管理器"""
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.prompts_dir.mkdir(exist_ok=True)
        
    def get_available_prompts(self) -> List[str]:
        """獲取可用的 Prompt 列表"""
        try:
            if not self.prompts_dir.exists():
                return ["通用分析師"]
            
            prompt_files = []
            for file_path in self.prompts_dir.glob("*.txt"):
                # 移除副檔名，使用檔案名作為 prompt 名稱
                prompt_name = file_path.stem
                prompt_files.append(prompt_name)
            
            # 如果沒有找到任何檔案，返回預設選項
            if not prompt_files:
                return ["通用分析師"]
                
            # 按字母順序排序，但將通用分析師放在最前面
            prompt_files.sort()
            if "通用分析師" in prompt_files:
                prompt_files.remove("通用分析師")
                prompt_files.insert(0, "通用分析師")
                
            return prompt_files
            
        except Exception as e:
            print(f"獲取 Prompt 列表時發生錯誤: {e}")
            return ["通用分析師"]
    
    def get_prompt_content(self, prompt_name: str) -> str:
        """獲取指定 Prompt 的內容"""
        try:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                # 如果檔案不存在，返回預設的通用 prompt
                return self._get_default_prompt()
                
        except Exception as e:
            print(f"讀取 Prompt 檔案時發生錯誤: {e}")
            return self._get_default_prompt()
    
    def save_prompt(self, prompt_name: str, content: str) -> bool:
        """保存 Prompt 內容到檔案"""
        try:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"保存 Prompt 檔案時發生錯誤: {e}")
            return False
    
    def delete_prompt(self, prompt_name: str) -> bool:
        """刪除指定的 Prompt 檔案"""
        try:
            # 不允許刪除通用分析師
            if prompt_name == "通用分析師":
                return False
                
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            
            if prompt_file.exists():
                prompt_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"刪除 Prompt 檔案時發生錯誤: {e}")
            return False
    
    def get_prompt_info(self) -> Dict[str, Dict]:
        """獲取所有 Prompt 的詳細信息"""
        prompts_info = {}
        
        for prompt_name in self.get_available_prompts():
            try:
                prompt_file = self.prompts_dir / f"{prompt_name}.txt"
                
                if prompt_file.exists():
                    file_stats = prompt_file.stat()
                    content = self.get_prompt_content(prompt_name)
                    
                    prompts_info[prompt_name] = {
                        "file_size": file_stats.st_size,
                        "modified_time": file_stats.st_mtime,
                        "content_length": len(content),
                        "word_count": len(content.split()),
                        "description": self._extract_description(content)
                    }
                else:
                    prompts_info[prompt_name] = {
                        "file_size": 0,
                        "modified_time": 0,
                        "content_length": 0,
                        "word_count": 0,
                        "description": "預設 Prompt"
                    }
                    
            except Exception as e:
                print(f"獲取 {prompt_name} 信息時發生錯誤: {e}")
                
        return prompts_info
    
    def _extract_description(self, content: str) -> str:
        """從 Prompt 內容中提取描述"""
        try:
            lines = content.split('\n')
            # 查找第一行非空白的內容作為描述
            for line in lines:
                line = line.strip()
                if line and not line.startswith('**') and not line.startswith('#'):
                    return line[:100] + "..." if len(line) > 100 else line
            return "無描述"
        except:
            return "無描述"
    
    def _get_default_prompt(self) -> str:
        """獲取預設的 Prompt 內容"""
        return """你是一位通用的內容分析專家，能夠針對各種類型的影片內容提供專業的分析和見解。

請根據以下 YouTube 影片內容，撰寫一份綜合性的內容分析報告：

**報告要求：**
1. **內容摘要**：簡潔地總結影片的主要內容和核心信息
2. **主題分析**：深入分析影片討論的主題和觀點
3. **結構評估**：評估內容的組織結構和邏輯流程
4. **價值提取**：提取影片中的有價值信息和見解
5. **受眾分析**：分析目標受眾和內容適用性
6. **綜合評價**：提供整體評價和改進建議

**撰寫風格：**
- 保持客觀中立的分析態度
- 使用清晰專業的表達方式
- 提供具體的例證和支持
- 平衡深度分析與可讀性

**報告結構：**
1. 內容概要
2. 主題與觀點分析
3. 結構與邏輯評估
4. 關鍵信息提取
5. 受眾與影響分析
6. 總結與建議

請提供全面、客觀的內容分析，幫助深入理解影片的價值和意義。"""
