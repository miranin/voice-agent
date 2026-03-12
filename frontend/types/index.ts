export interface Source {
  title: string;
  url: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
}

export interface VoiceQueryResponse {
  transcript: string;
  response_text: string;
  audio_url: string;
}
