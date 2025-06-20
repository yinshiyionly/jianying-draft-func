#!/usr/bin/env python3
"""
剪映草稿生成脚本 - 改进版
提供类接口供调用，支持配置文件方式生成剪映草稿
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
import pyJianYingDraftMixed as draft
from pyJianYingDraftMixed import Intro_type, Transition_type, trange, tim

class JianYingDraftGenerator:
    """剪映草稿生成器"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        """
        初始化草稿生成器
        
        Args:
            width: 视频宽度
            height: 视频高度
        """
        self.width = width
        self.height = height
        self.script = None
        
    def create_script(self, has_audio=False, has_video=False, has_text=False, has_voice=False) -> None:
        """
        创建剪映草稿脚本
        
        Args:
            has_audio: 是否需要音频轨道
            has_video: 是否需要视频轨道
            has_text: 是否需要文本轨道
            has_voice: 是否需要配音轨道（包括配音和字幕）
        """
        try:
            self.script = draft.Script_file(self.width, self.height)
            # 根据参数添加相应轨道
            if has_audio:
                # 背景音乐也是音频轨道类型，需要指定 track_name 为 "background"
                self.script.add_track(draft.Track_type.audio, track_name="background")
                print("已添加音频轨道")
            if has_voice:
                # 配音也是音频轨道类型，需要指定 track_name 为 "voice"
                self.script.add_track(draft.Track_type.audio, track_name="voice")
                print("已添加配音轨道")
            if has_video:
                self.script.add_track(draft.Track_type.video)
                print("已添加视频轨道")
            if has_text:
                self.script.add_track(draft.Track_type.text)
                print("已添加文本轨道")
            print(f"成功创建 {self.width}x{self.height} 分辨率的草稿脚本")
        except Exception as e:
            raise RuntimeError(f"创建草稿脚本失败: {e}")
    
    def validate_video_data(self, video_data: Dict[str, Any]) -> bool:
        """
        验证视频数据的有效性
        
        Args:
            video_data: 视频数据字典
            
        Returns:
            bool: 数据是否有效
        """
        required_fields = ['origin_name', 'duration']
        for field in required_fields:
            if field not in video_data:
                print(f"警告: 视频数据缺少必要字段 '{field}': {video_data}")
                return False
        
        # 验证duration是否为有效数字
        try:
            # 新的JSON格式中duration可能是浮点数
            duration = float(video_data['duration'])
            if duration <= 0:
                print(f"警告: 视频时长无效 (duration={duration}): {video_data}")
                return False
        except (ValueError, TypeError):
            print(f"警告: 视频时长格式错误: {video_data}")
            return False
            
        return True
        
    def validate_voice_data(self, voice_data: Dict[str, Any]) -> bool:
        """
        验证配音数据的有效性
        
        Args:
            voice_data: 配音数据字典
            
        Returns:
            bool: 数据是否有效
        """
        required_fields = ['voice_origin_name', 'voice_duration', 'srt_origin_name']
        for field in required_fields:
            if field not in voice_data:
                print(f"警告: 配音数据缺少必要字段 '{field}': {voice_data}")
                return False
        
        # 验证voice_duration是否为有效数字
        try:
            duration = float(voice_data['voice_duration'])
            if duration <= 0:
                print(f"警告: 配音时长无效 (voice_duration={duration}): {voice_data}")
                return False
        except (ValueError, TypeError):
            print(f"警告: 配音时长格式错误: {voice_data}")
            return False
            
        return True
    
    def add_video_segment(self, video_path: str, start_time: str, duration: float, 
                         volume: float = 1.0, add_transition: bool = False) -> Optional[draft.Video_segment]:
        """
        添加视频片段
        
        Args:
            video_path: 视频文件路径
            start_time: 开始时间 (如 "0s")
            duration: 持续时间 (秒)，浮点数
            volume: 音量 (0.0-1.0)
            add_transition: 是否添加转场效果
            
        Returns:
            Video_segment: 创建的视频片段，失败返回None
        """
        try:
            if not os.path.exists(video_path):
                print(f"错误: 视频文件不存在: {video_path}")
                return None
            
            video_material = draft.Video_material(video_path)
            video_segment = draft.Video_segment(
                video_material,
                trange(start_time, f"{duration:.4f}s"),  # 保留4位小数
                volume=volume
            )
            
            # todo 暂不支持转场特效
            # if add_transition:
            #     video_segment.add_transition(Transition_type.信号故障)
            
            self.script.add_segment(video_segment)
            print(f"成功添加视频: {os.path.basename(video_path)}, 开始时间: {start_time}, 时长: {duration}s")
            return video_segment
            
        except Exception as e:
            print(f"错误: 添加视频片段失败 {video_path}: {e}")
            return None
    
    def add_audio_segment(self, audio_path: str, start_time: str, duration: float,
                         volume: float = 0.5) -> Optional[draft.Audio_segment]:
        """
        添加音频片段
        
        Args:
            audio_path: 音频文件路径
            start_time: 开始时间 (如 "0s")
            duration: 持续时间 (秒)，浮点数
            volume: 音量 (0.0-1.0)
            
        Returns:
            Audio_segment: 创建的音频片段，失败返回None
        """
        try:
            if not os.path.exists(audio_path):
                print(f"错误: 音频文件不存在: {audio_path}")
                return None
            
            audio_material = draft.Audio_material(audio_path)
            audio_segment = draft.Audio_segment(
                audio_material,
                trange(start_time, f"{duration:.4f}s"),  # 保留4位小数
                volume=volume
            )
            
            self.script.add_segment(audio_segment, track_name="background")
            print(f"成功添加音频: {os.path.basename(audio_path)}, 开始时间: {start_time}, 时长: {duration}s")
            return audio_segment
            
        except Exception as e:
            print(f"错误: 添加音频片段失败 {audio_path}: {e}")
            return None
        
    def add_voice_segment(self, audio_path: str, start_time: str, duration: float,
                         volume: float = 1.0) -> Optional[draft.Audio_segment]:
        """
        添加音频片段
        
        Args:
            audio_path: 音频文件路径
            start_time: 开始时间 (如 "0s")
            duration: 持续时间 (秒)，浮点数
            volume: 音量 (0.0-1.0)
            
        Returns:
            Audio_segment: 创建的音频片段，失败返回None
        """
        try:
            if not os.path.exists(audio_path):
                print(f"错误: 音频文件不存在: {audio_path}")
                return None
            
            audio_material = draft.Audio_material(audio_path)
            audio_segment = draft.Audio_segment(
                audio_material,
                trange(start_time, f"{duration:.4f}s"),  # 保留4位小数
                volume=volume
            )
            
            self.script.add_segment(audio_segment, track_name="voice")
            print(f"成功添加音频: {os.path.basename(audio_path)}, 开始时间: {start_time}, 时长: {duration}s")
            return audio_segment
            
        except Exception as e:
            print(f"错误: 添加音频片段失败 {audio_path}: {e}")
            return None
    
    def add_text_segment(self, text: str, timerange: Any, font_type: str = "文轩体",
                        color: tuple = (1.0, 1.0, 0.0), position_y: float = -0.8) -> Optional[draft.Text_segment]:
        """
        添加文本片段
        
        Args:
            text: 文本内容
            timerange: 时间范围
            font_type: 字体类型
            color: 文字颜色 RGB
            position_y: Y轴位置
            
        Returns:
            Text_segment: 创建的文本片段，失败返回None
        """
        try:
            text_segment = draft.Text_segment(
                text, timerange,
                font=getattr(draft.Font_type, font_type, draft.Font_type.文轩体),
                style=draft.Text_style(color=color),
                clip_settings=draft.Clip_settings(transform_y=position_y)
            )
            
            # 添加出场动画
            text_segment.add_animation(draft.Text_outro.故障闪动, duration=tim("1s"))
            # 添加文本气泡效果和花字效果 (可选)
            text_segment.add_bubble("361595", "6742029398926430728")
            text_segment.add_effect("7296357486490144036")
            
            self.script.add_segment(text_segment)
            print(f"成功添加文本: {text}")
            return text_segment
            
        except Exception as e:
            print(f"错误: 添加文本片段失败: {e}")
            return None
    
    def process_video_data_list(self, video_data_list: List[Dict], asset_dir: str) -> bool:
        """
        批量处理视频数据列表
        
        Args:
            video_data_list: 视频数据列表
            asset_dir: 素材目录路径
            
        Returns:
            bool: 处理是否成功
        """
        if not video_data_list:
            print("警告: 视频数据列表为空")
            return True
        
        current_start_seconds = 0
        last_video_segment = None
        
        for i, video_data in enumerate(video_data_list):
            if not self.validate_video_data(video_data):
                print(f"跳过无效的视频数据 (第{i+1}个)")
                continue
            
            video_name = video_data['origin_name']
            video_path = os.path.join(asset_dir, video_name)
            
            # 使用 get_media_duration 获取准确的视频时长
            video_duration = self.get_media_duration(video_path)
            if video_duration <= 0:
                print(f"跳过时长无效的视频: {video_name}")
                continue
            
            start_time = f"{current_start_seconds}s"
            # add_transition = (i > 0)  # 第一个视频不加转场
            
            video_segment = self.add_video_segment(
                video_path, start_time, video_duration,
                volume=1.0
            )
            
            if video_segment:
                last_video_segment = video_segment
                current_start_seconds += video_duration
            else:
                print(f"跳过失败的视频: {video_name}")
        
        return last_video_segment is not None
    
    def process_audio_data_list(self, audio_data_list: List[Dict], asset_dir: str) -> bool:
        """
        批量处理音频数据列表
        
        Args:
            audio_data_list: 音频数据列表
            asset_dir: 素材目录路径
            
        Returns:
            bool: 处理是否成功
        """
        if not audio_data_list:
            print("提示: 音频数据列表为空，跳过音频处理")
            return True
        
        current_start_seconds = 0
        
        for i, audio_data in enumerate(audio_data_list):
            if not self.validate_video_data(audio_data):  # 复用验证方法
                print(f"跳过无效的音频数据 (第{i+1}个)")
                continue
            
            audio_name = audio_data['origin_name']
            audio_path = os.path.join(asset_dir, audio_name)
            
            # 使用 get_media_duration 获取准确的音频时长
            audio_duration = self.get_media_duration(audio_path)
            if audio_duration <= 0:
                print(f"跳过时长无效的音频: {audio_name}")
                continue
            
            start_time = f"{current_start_seconds}s"
            
            audio_segment = self.add_audio_segment(
                audio_path, start_time, audio_duration, volume=0.5
            )
            
            if audio_segment:
                current_start_seconds += audio_duration
            else:
                print(f"跳过失败的音频: {audio_name}")
        
        return True
        
    def process_voice_data_list(self, voice_data_list: List[Dict], asset_dir: str) -> bool:
        """
        批量处理配音数据列表，包括配音和对应的字幕
        
        Args:
            voice_data_list: 配音数据列表
            asset_dir: 素材目录路径
            
        Returns:
            bool: 处理是否成功
        """
        if not voice_data_list:
            print("提示: 配音数据列表为空，跳过配音处理")
            return True
        
        current_start_seconds = 0
        
        for i, voice_data in enumerate(voice_data_list):
            if not self.validate_voice_data(voice_data):
                print(f"跳过无效的配音数据 (第{i+1}个)")
                continue
            
            # 1. 处理配音文件
            voice_name = voice_data['voice_origin_name']
            voice_path = os.path.join(asset_dir, voice_name)
            
            # 使用 get_media_duration 获取准确的配音时长
            voice_duration = self.get_media_duration(voice_path)
            if voice_duration <= 0:
                print(f"跳过时长无效的配音: {voice_name}")
                continue
            
            start_time = f"{current_start_seconds}s"
            
            # 配音音量可以设置得稍大一些，以便突出配音
            voice_segment = self.add_voice_segment(
                voice_path, start_time, voice_duration, volume=1.0
            )
            
            # 2. 处理字幕文件
            srt_name = voice_data['srt_origin_name']
            srt_path = os.path.join(asset_dir, srt_name)
            
            if os.path.exists(srt_path):
                try:
                    # 导入字幕，使用配音时长作为时间偏移
                    time_offset = f"{current_start_seconds}s"
                    self.script.import_srt(
                        srt_path,
                        track_name="subtitle",
                        time_offset=time_offset,
                        text_style=draft.Text_style(size=12.0, color=(1.0, 1.0, 1.0)),
                        clip_settings=draft.Clip_settings(transform_y=0.5)
                    )
                    print(f"成功导入字幕: {srt_name}, 时间偏移: {time_offset}")
                except Exception as e:
                    print(f"导入字幕文件失败 {srt_name}: {e}")
            else:
                print(f"警告: 字幕文件不存在: {srt_path}")
            
            if voice_segment:
                current_start_seconds += voice_duration
            else:
                print(f"跳过失败的配音: {voice_name}")
        
        return True
    
    def save_draft(self, output_path: str) -> bool:
        """
        保存草稿到指定路径
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not self.script:
                raise RuntimeError("草稿脚本未初始化")
            
            if output_path and not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)
            # 兼容 windows 的草稿文件名 draft_content.json
            self.script.dump(os.path.join(output_path, "draft_content.json"))
            print(f"win-草稿内容已成功保存到: {os.path.join(output_path, 'draft_content.json')}")


            # 兼容 macos 的草稿文件名 draft_info.json
            self.script.dump(os.path.join(output_path, "draft_info.json"))
            print(f"mac-草稿内容已成功保存到: {os.path.join(output_path, 'draft_info.json')}")

            # 创建 draft_meta_info.json 空文件，减少手动创建空草稿的步骤
            with open(os.path.join(output_path, "draft_meta_info.json"), "w") as f:
                f.write("")
                print(f"草稿元信息已成功保存到: {os.path.join(output_path, 'draft_meta_info.json')}")
            
            return True
            
        except Exception as e:
            print(f"错误: 保存草稿失败: {e}")
            return False

    def get_media_duration(self, file_path: str) -> float:
        """
        使用 pymediainfo 计算媒体文件的精确时长
        
        Args:
            file_path: 媒体文件路径
            
        Returns:
            float: 媒体文件时长(秒)，保留4位小数，如果计算失败则返回0.0
        """
        try:
            if not os.path.exists(file_path):
                print(f"错误: 文件不存在: {file_path}")
                return 0.0
            
            from pymediainfo import MediaInfo
            media_info = MediaInfo.parse(file_path)
            
            # 优先使用 General track 的 duration
            for track in media_info.tracks:
                if track.track_type == "General":
                    if track.duration is not None:
                        # print(f"文件时长: {track.duration} 文件路径: {file_path}")
                        # MediaInfo 的 duration 是毫秒单位，需要转换为秒
                        return round(float(track.duration) / 1000, 4)
            
            # 如果 General track 中没有 duration，尝试其他轨道
            for track in media_info.tracks:
                if track.duration is not None:
                    return round(float(track.duration) / 1000, 4)
                
            print(f"警告: 无法获取文件时长: {file_path}")
            return 0.0
            
        except Exception as e:
            print(f"错误: 计算文件时长失败 {file_path}: {e}")
            return 0.0


class JianYingDraftService:
    """剪映草稿服务类，提供简单的API接口"""
    
    def __init__(self):
        """初始化服务"""
        self.generator = None
        
    def generate_from_config(self, draft_path: str, video_segment: List[Dict] = None, 
                           bgm_segment: List[Dict] = None, voice_segment: List[Dict] = None,
                           width: int = 1080, height: int = 1920, text: str = '') -> Tuple[bool, str]:
        """
        从传入的配置参数生成剪映草稿
        
        Args:
            draft_path: 草稿箱目录绝对路径
            video_segment: 视频片段属性列表
            bgm_segment: 背景音乐片段属性列表
            voice_segment: 配音和字幕片段属性列表
            width: 视频宽度，默认1080
            height: 视频高度，默认1920
            text: 文本内容，默认为空
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
                - 如果成功，返回 (True, "")
                - 如果失败，返回 (False, 错误信息)
        """
        try:
            print("=" * 50)
            print("剪映草稿生成脚本 - 开始执行")
            print("=" * 50)
            
            # 初始化参数
            video_data_list = video_segment or []
            audio_data_list = bgm_segment or []
            voice_data_list = voice_segment or []
            
            # 素材目录是 draft_path 下的一级文件夹-miaobi
            material_dir = os.path.join(draft_path, "miaobi")
            
            print(f"从配置文件读取: 视频数据 {len(video_data_list)}项, 音频数据 {len(audio_data_list)}项, 配音数据 {len(voice_data_list)}项")
            
            # 规范化路径
            try:
                material_dir = self._normalize_path(material_dir)
                draft_path = self._normalize_path(draft_path)
            except Exception as e:
                return False, f"路径规范化失败: {str(e)}"
            
            # 验证路径
            if not self._validate_paths(draft_path, material_dir):
                return False, "草稿箱或素材目录路径验证失败"
            
            # 确定是否需要各种轨道
            has_audio = bool(audio_data_list)
            has_video = bool(video_data_list)
            has_voice = bool(voice_data_list)
            has_text = bool(text and video_data_list)  # 只有当有文本内容且有视频时才添加文本轨道
            
            print(f"视频数据: {len(video_data_list)}项")
            print(f"音频数据: {len(audio_data_list)}项")
            print(f"配音数据: {len(voice_data_list)}项")
            print(f"草稿分辨率: {width}x{height}")
            
            # 检查是否有任何媒体数据
            has_any_media = has_audio or has_voice or has_video
            
            if not has_any_media:
                return False, "没有任何媒体数据(视频/音频/配音)，不创建草稿"
            
            # 创建草稿生成器
            try:
                self.generator = JianYingDraftGenerator(width, height)
                self.generator.create_script(has_audio=has_audio, has_video=has_video, has_text=has_text, has_voice=has_voice)
            except Exception as e:
                return False, f"创建草稿生成器失败: {str(e)}"
            
            # 处理音频数据
            if has_audio:
                try:
                    if not self.generator.process_audio_data_list(audio_data_list, material_dir):
                        print("警告: 音频处理出现问题，但继续执行")
                except Exception as e:
                    return False, f"处理音频数据失败: {str(e)}"
            else:
                print("没有音频数据，跳过音频轨道处理")
                
            # 处理配音数据
            if has_voice:
                try:
                    if not self.generator.process_voice_data_list(voice_data_list, material_dir):
                        print("警告: 配音处理出现问题，但继续执行")
                except Exception as e:
                    return False, f"处理配音数据失败: {str(e)}"
            else:
                print("没有配音数据，跳过配音轨道处理")
            
            # 处理视频数据
            if has_video:
                try:
                    if not self.generator.process_video_data_list(video_data_list, material_dir):
                        return False, "视频处理失败"
                except Exception as e:
                    return False, f"处理视频数据失败: {str(e)}"
            else:
                print("没有视频数据，跳过视频轨道处理")
            
            # 添加文本片段 (如果有视频和文本内容)
            if has_text:
                try:
                    # 计算总时长作为文本时间范围
                    total_duration = sum(float(v.get('duration', 0)) for v in video_data_list 
                                       if self.generator.validate_video_data(v))
                    if total_duration > 0:
                        text_timerange = trange("0s", f"{total_duration:.4f}s")  # 保留两位小数
                        if not self.generator.add_text_segment(text, text_timerange):
                            return False, "添加文本片段失败"
                except Exception as e:
                    return False, f"处理文本数据失败: {str(e)}"
            elif text and not video_data_list:
                print("有文本内容但没有视频数据，无法添加文本片段")
            
            # 保存草稿
            try:
                if not self.generator.save_draft(draft_path):
                    return False, "保存草稿失败"
            except Exception as e:
                return False, f"保存草稿时发生错误: {str(e)}"
            
            print("=" * 50)
            print("草稿生成完成!")
            print("=" * 50)
            return True, ""
            
        except Exception as e:
            error_msg = f"生成草稿时发生未预期的错误: {str(e)}"
            print(error_msg)
            return False, error_msg
            
    def _normalize_path(self, path: str) -> str:
        """
        规范化文件路径，处理不同操作系统的路径格式
        
        Args:
            path: 原始路径
            
        Returns:
            str: 规范化后的路径
        """
        # 替换反斜杠为正斜杠
        path = path.replace('\\', '/')
        
        # 处理Windows路径中的冒号
        if ':' in path and not path.startswith('/'):
            # Windows路径格式：C:/Users/...
            return path
        
        return path
        
    def _validate_paths(self, draft_path: str, asset_dir: str) -> bool:
        """
        验证路径的有效性
        
        Args:
            draft_path: 草稿箱绝对路径
            asset_dir: 素材目录路径
            
        Returns:
            bool: 路径是否有效
        """
        try:
            # 基本路径检查
            if not draft_path or draft_path.endswith('/') or draft_path.endswith('\\') and not os.path.isdir(asset_dir):
                print(f"错误: 草稿箱目录路径无效: {draft_path}")
                return False
                
            if not asset_dir or not (asset_dir.endswith('/') or asset_dir.endswith('\\')) and not os.path.isdir(asset_dir):
                print(f"错误: 素材目录路径无效: {asset_dir}")
                return False
            
            # 验证草稿箱目录
            if not os.path.exists(draft_path):
                print(f"错误: 草稿箱目录不存在: {draft_path}")
                return False
            else:
                print(f"草稿箱目录检查通过: {draft_path}")

            # 验证素材目录
            if not os.path.exists(asset_dir):
                print(f"错误: 素材目录不存在: {asset_dir}")
                return False
            else:
                print(f"素材目录检查通过: {asset_dir}")
                
            # 创建草稿箱目录
            if draft_path and not os.path.exists(draft_path):
                try:
                    os.makedirs(draft_path, exist_ok=True)
                    print(f"创建草稿箱目录: {draft_path}")
                except Exception as e:
                    print(f"错误: 无法创建草稿箱目录 {draft_path}: {e}")
                    return False

            # 创建素材目录
            if asset_dir and not os.path.exists(asset_dir):
                try:
                    os.makedirs(asset_dir, exist_ok=True)
                    print(f"创建素材目录: {asset_dir}")
                except Exception as e:
                    print(f"错误: 无法创建素材目录 {asset_dir}: {e}")
                    return False
            
            # 检查草稿箱目录是否可写
            try:
                # 检查目录是否可写
                test_file = os.path.join(draft_path, '.write_test_temp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                print(f"错误: 输出目录不可写: {draft_path}: {e}")
                return False
            
            # 检查素材目录是否可写
            try:
                # 检查目录是否可写
                test_file = os.path.join(asset_dir, '.write_test_temp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                print(f"错误: 输出目录不可写: {asset_dir}: {e}")
                return False
                
            print(f"草稿箱目录检查通过: {draft_path}")
            print(f"素材目录检查通过: {asset_dir}")
            return True
        except Exception as e:
            print(f"路径验证过程中出现错误: {e}")
            return False

if __name__ == "__main__":
    # 创建服务实例
    service = JianYingDraftService()
    
    # 示例配置
    draft_path = "./demo"
    video_segment = [
        {
            "origin_name": "video1.mp4",
            "duration": 10.5
        },
        {
            "origin_name": "video2.mp4",
            "duration": 10.5
        }
    ]
    bgm_segment = [
        {
            "origin_name": "bgm1.mp3",
            "duration": 30.0
        },
        {
            "origin_name": "bgm2.mp3",
            "duration": 30.0
        }
    ]
    voice_segment = [
        {
            "voice_origin_name": "voice1.wav",
            "voice_duration": 5.0,
            "srt_origin_name": "srt1.srt"
        },
        {
            "voice_origin_name": "voice2.wav",
            "voice_duration": 5.0,
            "srt_origin_name": "srt2.srt"
        }
    ]
    
    # 从参数生成草稿
    success, error_msg = service.generate_from_config(
        draft_path=draft_path,
        video_segment=video_segment,
        bgm_segment=bgm_segment,
        voice_segment=voice_segment,
        width=1080,
        height=1920
    )

    if success:
        print("草稿生成成功")
    else:
        print(f"草稿生成失败: {error_msg}")