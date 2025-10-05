import axios from 'axios';

export const createSocketConnection = () => {
    const socket = new WebSocket(import.meta.env.VITE_WS_URL);
    return socket;
}

export const sendImageFile = async (file) => {
    const formData = new FormData()
    formData.append('image', file)

    try {
        // Send formData to backend for processing
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/upload_image`,
            formData, { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        return response.data;
    }
    catch (error) {
        console.error('Error uploading image:', error);
        throw error;
    }

    return response.data;
}