from dataclasses import dataclass


@dataclass
class DataOfProcess:
    video_name: str
    fps: int
    avg_time_of_frame_with_txt_s: int
    number_of_pages_with_text: int
    script_running_time: int
    start_at: str
    end_at: str
    report_created_at: str

    @property
    def get_video_name(self) -> str:
        key = 'Video name: '
        return key + str(self.video_name)

    @property
    def get_fps(self) -> str:
        key = 'FPS: '
        return key + str(self.fps)

    @property
    def get_avg_time_of_frame_with_txt_s(self) -> str:
        key = 'Average processing time of one frame with text [sec]: '
        return key + str(self.avg_time_of_frame_with_txt_s)

    @property
    def get_number_of_pages_with_text(self) -> str:
        key = 'Number of pages with found text: '
        return key + str(self.number_of_pages_with_text)

    @property
    def get_script_running_time(self) -> str:
        key = 'Script running time [sec]: '
        return key + str(self.script_running_time)

    @property
    def get_start_at(self) -> str:
        key = 'Video started form: '
        return key + str(self.start_at)

    @property
    def get_end_at(self) -> str:
        key = 'Video ended to: '
        return key + str(self.end_at)

    @property
    def get_report_created_at(self) -> str:
        key = 'Report created at [UTC]: '
        return key + str(self.report_created_at)

    @property
    def get_list_of_entry(self):
        return [
            self.get_video_name,
            self.get_fps,
            self.get_avg_time_of_frame_with_txt_s,
            self.get_number_of_pages_with_text,
            self.get_script_running_time,
            self.get_start_at,
            self.get_end_at,
            self.get_report_created_at
        ]

    @property
    def get_str_to_save(self) -> str:
        resp = '\n'.join(self.get_list_of_entry)
        return resp