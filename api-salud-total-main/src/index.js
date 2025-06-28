import 'dotenv/config';
import app from './app.js';
console.log('RESEND_API_KEY:', process.env.RESEND_API_KEY);

const PORT = process.env.PORT || 4000;

app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
