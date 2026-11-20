import json
import re
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from .views import buat_simulasi_harga, index, panggil_api_ai, prediksi_harga_ribu


class ModelPrediksiStub:
    def __init__(self):
        self.inputs = []

    def predict(self, data):
        self.inputs.append(data.copy())
        return [
            data["jarak_km"].iloc[0] * 100
            + data["rating"].iloc[0] * 10
            + data["ac_num"].iloc[0] * 50
        ]


class SimulasiHargaTests(SimpleTestCase):
    def test_simulasi_menggunakan_model_dengan_parameter_terbaru(self):
        model = ModelPrediksiStub()
        jarak = 3.7
        rating = 4.8
        ac_num = 0
        harga_utama = prediksi_harga_ribu(model, jarak, rating, ac_num)

        simulasi = buat_simulasi_harga(model, jarak, rating, ac_num, harga_utama)

        self.assertEqual(
            [titik["jarak_km"] for titik in simulasi],
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.7, 4.0, 5.0],
        )
        self.assertEqual(
            simulasi[6]["harga_rupiah"],
            int(round(harga_utama * 1000)),
        )
        self.assertTrue(all(data["rating"].iloc[0] == rating for data in model.inputs))
        self.assertTrue(all(data["ac_num"].iloc[0] == ac_num for data in model.inputs))
        self.assertEqual(len(model.inputs), len(simulasi))

    def test_simulasi_ikut_berubah_saat_ac_dan_rating_berubah(self):
        model = ModelPrediksiStub()
        prediksi_ac = buat_simulasi_harga(
            model, 1.5, 4.2, 1, prediksi_harga_ribu(model, 1.5, 4.2, 1)
        )
        prediksi_non_ac = buat_simulasi_harga(
            model, 1.5, 4.8, 0, prediksi_harga_ribu(model, 1.5, 4.8, 0)
        )

        self.assertNotEqual(
            [titik["harga_rupiah"] for titik in prediksi_ac],
            [titik["harga_rupiah"] for titik in prediksi_non_ac],
        )

    def test_prediksi_negatif_dibatasi_ke_nol(self):
        class NegativeModel:
            def predict(self, data):
                return [-10]

        self.assertEqual(prediksi_harga_ribu(NegativeModel(), 2.0, 4.0, 1), 0.0)


class GrafikSimulasiViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def render_request(self, method, data=None):
        request = getattr(self.factory, method)("/", data or {})
        request.session = {}
        with (
            patch("prediksi.views.RiwayatPrediksi.objects.create"),
            patch("prediksi.views.RiwayatPrediksi.objects.order_by", return_value=[]),
            patch("prediksi.views.RiwayatPrediksi.objects.count", return_value=0),
        ):
            response = index(request)
        return response.content.decode("utf-8")

    def simulation_from(self, html):
        match = re.search(r"const simulationData = (.+);", html)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_chart_hanya_muncul_setelah_prediksi_berhasil(self):
        halaman = self.render_request("get")
        halaman_error = self.render_request("post", {
            "aksi": "hitung",
            "jarak_km": "30",
            "ac": "ya",
            "rating": "4.2",
        })

        self.assertNotIn('id="simulasiHargaChart"', halaman)
        self.assertNotIn('id="simulasiHargaChart"', halaman_error)
        self.assertIn('id="scatterTarifChart"', halaman)
        self.assertIn('id="barAcChart"', halaman)
        self.assertEqual(len(re.findall(
            r'class="(?:result-panel )?calculator-frame(?: [^"]*)?"',
            halaman,
        )), 3)

    def test_kalkulasi_ulang_mengirim_simulasi_dan_menandai_jarak_input(self):
        dasar = self.render_request("post", {
            "aksi": "hitung", "jarak_km": "1.5", "ac": "ya", "rating": "4.2",
        })
        jarak_berubah = self.render_request("post", {
            "aksi": "hitung", "jarak_km": "3", "ac": "ya", "rating": "4.2",
        })
        ac_berubah = self.render_request("post", {
            "aksi": "hitung", "jarak_km": "1.5", "ac": "tidak", "rating": "4.2",
        })
        rating_berubah = self.render_request("post", {
            "aksi": "hitung", "jarak_km": "1.5", "ac": "ya", "rating": "4.8",
        })
        simulasi_dasar = self.simulation_from(dasar)

        self.assertIn('id="simulasiHargaChart"', dasar)
        self.assertEqual(dasar.count('id="simulasiHargaChart"'), 1)
        self.assertIn('id="simulationTrend"', dasar)
        self.assertIn('id="simulationPriceChange"', dasar)
        self.assertIn('id="simulationConclusion"', dasar)
        self.assertIn("const priceChange = endPoint.harga_rupiah - startPoint.harga_rupiah;", dasar)
        self.assertEqual(simulasi_dasar[2]["jarak_km"], 1.5)
        self.assertIn("index === selectedPointIndex", dasar)
        self.assertIn("const selectedDistance = 1.5;", dasar)
        self.assertIn("const selectedDistance = 3.0;", jarak_berubah)
        self.assertEqual(simulasi_dasar, self.simulation_from(jarak_berubah))
        self.assertNotEqual(simulasi_dasar, self.simulation_from(ac_berubah))
        self.assertNotEqual(simulasi_dasar, self.simulation_from(rating_berubah))


class PanggilApiAiTests(SimpleTestCase):
    @patch("prediksi.views.urllib.request.urlopen")
    def test_groq_uses_current_model_and_completion_token_parameter(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Analisis harga kos."}}],
        }).encode("utf-8")

        result = panggil_api_ai("groq", "test-api-key", "Periksa harga kos.")

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(result, "Analisis harga kos.")
        self.assertEqual(payload["model"], "openai/gpt-oss-20b")
        self.assertEqual(payload["max_completion_tokens"], 220)
        self.assertNotIn("max_tokens", payload)
