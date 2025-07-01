# imagegen/views.py - COMPLETE FIXED VERSION

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import GeneratedImage, UsageSession
from .face_match import match_face
from faceswap.huggingface_utils import FaceFusionClient
import tempfile
import base64
from django.core.files.base import ContentFile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
import time
import random
from django.core.cache import cache
from .utils import compress_image


# 🔥 NEW: Memory management settings
MAX_CONCURRENT_JOBS = 2  # Limit simultaneous face swaps

# Map historical figures to their Cloudinary URLs - UPDATED WITH 65+ FIGURES
HISTORICAL_FIGURES = {
    "Abraham Lincoln": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608917/Abraham_Lincoln_o5kbjh.png",
    "Alexander the Great": "https://res.cloudinary.com/dddye9wli/image/upload/v1749854959/alexander_the_great_j5icxu.png",
    "Andy Warhol": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608920/Andy_Warhol_p6lq5q.png",
    "Anne Frank": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608918/Anne_Frank_flivyh.png",
    "Audrey Hepburn": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608919/Audrey_Hepburn_rtw37d.png",
    "Benjamin Franklin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608919/Benjamin_Franklin_lh9vdd.png",
    "Beyonce": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Beyonce_ry9nep.png",
    "Bill Clinton": "https://res.cloudinary.com/dddye9wli/image/upload/v1750374687/Bill_Clinton_za0jbh.png",
    "Billie Holiday": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Billie_Holiday_zpq9ks.png",
    "Bob Dylan": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Bob_Dylan_soy4se.png",
    "Brittany Spears": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608923/Brittany_Spears_kdhdh3.png",
    "Che Guevara": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921229/Che_Guevara_kkrtcr.png",
    "Cher": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/cher_hhhcbg.png",
    "Christopher Columbus": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Christopher_columbus_oewf7p.png",
    "Cleopatra": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921359/cleopatra_zcslcx.png",
    "Coco Chanel": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/Coco_Chanel_dw4bcq.png",
    "Danny Devito": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Danny_Devito_ajkoal.png",
    "Donald Trump": "https://res.cloudinary.com/dddye9wli/image/upload/v1750550608/Donald_Trump_yqggmn.png",
    "Elon Musk": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Elon_Musk_c3ii8i.png",
    "Elvis": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921841/elvis_heazqa.png",
    "Elvisnotsinging": "https://res.cloudinary.com/dddye9wli/image/upload/v1749857225/elvisnotsinging_twnnta.png",
    "Frida Khalo": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/frida_khalo_gzibma.png",
    "Genghis Khan": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608927/Genghis_Khan_ewsfvk.png",
    "Hernan Cortes": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Hernan_Cortes_lfonsp.png",
    "JFK": "https://res.cloudinary.com/dddye9wli/image/upload/v1749856600/jfk_npw3lg.png",
    "James Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/james_dean_bhaaum.png",
    "Janis Joplin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Janis_Joplin_cl5pi8.png",
    "Jimi Hendrix": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921237/jimi_hendrix_fm56df.png",
    "Joan of Arc": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921237/Joan_of_Arc_bysrio.png",
    "John Lennon": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/John_Lennon_lod1zc.png",
    "Josephine Baker": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Josephine_Baker_spiswe.png",
    "Judy Garland": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608931/Judy_Garland_bfbss2.png",
    "Julius Cesear": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608931/Julius_Cesear_wampoh.png",
    "Karl Marx": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608934/Karl_Marx_hlmk0s.png",
    "Keith": "https://res.cloudinary.com/dddye9wli/image/upload/v1749856455/keith_o6fgff.png",
    "King Henry Vii": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/King_Henry_VII_wpclza.png",
    "Kylie Jenner": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Kylie_Jenner_vwasob.png",
    "Leonardo da Vinci": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921238/leonardo_davinci_wpggcn.png",
    "Lucille Ball": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Lucille_Ball_a5zjih.png",
    "Madonna": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Madonna_qlszs5.png",
    "Malcolm X": "https://res.cloudinary.com/dddye9wli/image/upload/v1749854991/malcolm_x_kwlnil.png",
    "Mao Zedong": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Mao_zedong_lpvr7v.png",
    "Marco Polo": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608937/Marco_Polo_mah3wb.png",
    "Marie Antoinette": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921242/Marie_Antoinette_f6ndp6.png",
    "Marilyn Manson": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608936/Marilyn_Manson_zwe6f7.png",
    "Marilyn Monroe": "https://res.cloudinary.com/dddye9wli/image/upload/v1749858269/marilyn_monroe_zhaxku.png",
    "Mark Zuckerberg": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608936/Mark_Zuckerberg_tvctxl.png",
    "Mona Lisa": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608976/Mona_Lisa_cwnwdk.png",
    "Napolean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749742732/napolean_azenei.png",
    "Oprah Winfrey": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608983/oprah_winfrey_c24nib.png",
    "Paula Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608987/Paula_Dean_lmyabz.png",
    "Pocahontas": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921243/Pocahontas_ys39zg.png",
    "Princess Diana": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921243/princess_diana_xcvc2a.png",
    "Queen Elizabeth I": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608993/Queen_Elizabeth_I_ct6ku4.png",
    "Queen Victoria": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609003/Queen_Victoria_jq4b9h.png",
    "Ragnar Lothbrok": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609005/Ragnar_Lothbrok_mwwutr.png",
    "Rasputin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Rasputin_kcpdi4.png",
    "Richard Nixon": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Richard_Nixon_qfgsnz.png",
    "Sigourney Weaver": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609007/Sigourney_Weaver_vn70qg.png",
    "Steve Jobs": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609007/Steve_Jobs_gluiyu.png",
    "Susan B Anthony": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Susan_B_Anthony_pgeomw.png",
    "Vladimir Putin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609009/Vladimir_Putin_u3k1st.png",
    "Xi Jinping": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609010/Xi_Jinping_tiyqx2.png",
    "Yoko Ono": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609010/Yoco_ono_ttzyo1.png",
}


class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Check server capacity
        active_jobs = cache.get('active_face_swap_jobs', 0)
        if active_jobs >= MAX_CONCURRENT_JOBS:
            return Response({"error": "Server busy. Try again in 30 seconds.", "retry_after": 30}, status=503)

        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=400)

        # 🔥 CRITICAL FIX: Get usage session from middleware OR create one
        usage_session = getattr(request, 'usage_session', None)
        
        # If no usage session from middleware, create one (fallback)
        if not usage_session and not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
                request.session.save()
            usage_session = UsageSession.get_or_create_for_session(request.session.session_key)
            print(f"🔧 Fallback: Created usage session for {request.session.session_key[:8]}...")
        
        # Compress image
        compressed_selfie = compress_image(selfie)
        selfie_content = compressed_selfie.read()
        selfie_for_model = InMemoryUploadedFile(
            file=io.BytesIO(selfie_content),
            field_name='selfie',
            name=f"compressed_{selfie.name}",
            content_type='image/jpeg',
            size=len(selfie_content),
            charset=None,
        )

        # Save to temp file for face matching
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(selfie_content)
            tmp_path = tmp.name

        temp_image = None
        try:
            # Increment job counter
            cache.set('active_face_swap_jobs', active_jobs + 1, timeout=300)
            
            # Face matching
            match_result = match_face(tmp_path)
            if "error" in match_result:
                return Response(match_result, status=status.HTTP_400_BAD_REQUEST)

            match_name = match_result["match_name"]
            match_score = match_result.get("score", 0)
            
            # Get historical image
            historical_image_url = HISTORICAL_FIGURES.get(match_name)
            if not historical_image_url:
                return Response({"error": f"No historical image available for {match_name}"}, status=400)

            # Create database record
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {match_name}",
                match_name=match_name,
                selfie=selfie_for_model,
                output_url="",
            )

            # Face swap
            class MockImageField:
                def __init__(self, url):
                    self.url = url

            source_mock = MockImageField(temp_image.selfie.url)
            target_mock = MockImageField(historical_image_url)

            client = FaceFusionClient()
            result_image_data = client.swap_faces(source_mock, target_mock)

            # Save result
            temp_image.output_image.save(
                f"{temp_image.id}_fused_{match_name.replace(' ', '_')}.jpg", 
                ContentFile(result_image_data)
            )
            temp_image.save()

            # 🔥 CRITICAL FIX: Update usage for anonymous users AFTER SUCCESS
            if usage_session and not request.user.is_authenticated:
                success = usage_session.use_match()
                print(f"📊 Usage updated - match used: {success}, new count: {usage_session.matches_used}/{usage_session.MAX_MATCHES}")

            return Response({
                "id": temp_image.id,
                "match_name": match_name,
                "match_score": round(match_score, 3),
                "message": f"Successfully transformed you into {match_name}!",
                "output_image_url": temp_image.output_image.url,
                "original_selfie_url": temp_image.selfie.url,
                "historical_figure_url": historical_image_url,
                "usage": self.get_usage_data(request, usage_session)
            })

        except Exception as e:
            if temp_image:
                try:
                    temp_image.delete()
                except:
                    pass
            return Response({"error": f"Face processing failed: {str(e)}"}, status=500)
        
        finally:
            current_jobs = cache.get('active_face_swap_jobs', 1)
            cache.set('active_face_swap_jobs', max(0, current_jobs - 1), timeout=300)
            try:
                os.unlink(tmp_path)
            except:
                pass

    def get_usage_data(self, request, usage_session):
        if request.user.is_authenticated:
            return {"unlimited": True}
        elif usage_session:
            return {
                "matches_used": usage_session.matches_used,
                "matches_limit": usage_session.MAX_MATCHES,
                "randomizes_used": usage_session.randomizes_used,
                "randomizes_limit": usage_session.MAX_RANDOMIZES,
                "can_match": usage_session.can_match,
                "can_randomize": usage_session.can_randomize,
                "is_limited": usage_session.is_limited,
            }
        return None


class RandomizeImageView(APIView):
    """Randomize with random historical figure - FIXED VERSION"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Check server capacity
        active_jobs = cache.get('active_face_swap_jobs', 0)
        if active_jobs >= MAX_CONCURRENT_JOBS:
            return Response({"error": "Server busy. Try again in 30 seconds.", "retry_after": 30}, status=503)

        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=400)

        # 🔥 CRITICAL FIX: Get usage session from middleware OR create one
        usage_session = getattr(request, 'usage_session', None)
        
        # If no usage session from middleware, create one (fallback)
        if not usage_session and not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
                request.session.save()
            usage_session = UsageSession.get_or_create_for_session(request.session.session_key)
            print(f"🔧 Fallback: Created usage session for {request.session.session_key[:8]}...")
        
        # Pick random figure
        random_figure = random.choice(list(HISTORICAL_FIGURES.keys()))
        historical_image_url = HISTORICAL_FIGURES[random_figure]
        
        # Compress image
        compressed_selfie = compress_image(selfie)
        selfie_content = compressed_selfie.read()
        selfie_for_model = InMemoryUploadedFile(
            file=io.BytesIO(selfie_content),
            field_name='selfie',
            name=f"compressed_{selfie.name}",
            content_type='image/jpeg',
            size=len(selfie_content),
            charset=None,
        )

        temp_image = None
        try:
            # Increment job counter
            cache.set('active_face_swap_jobs', active_jobs + 1, timeout=300)

            # Create database record
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {random_figure} (randomized)",
                match_name=random_figure,
                selfie=selfie_for_model,
                output_url="",
            )

            # Face swap
            class MockImageField:
                def __init__(self, url):
                    self.url = url

            source_mock = MockImageField(temp_image.selfie.url)
            target_mock = MockImageField(historical_image_url)

            client = FaceFusionClient()
            result_image_data = client.swap_faces(source_mock, target_mock)

            # Save result
            temp_image.output_image.save(
                f"{temp_image.id}_randomized_{random_figure.replace(' ', '_')}.jpg", 
                ContentFile(result_image_data)
            )
            temp_image.save()

            # 🔥 CRITICAL FIX: Update usage for anonymous users AFTER SUCCESS
            if usage_session and not request.user.is_authenticated:
                success = usage_session.use_randomize()
                print(f"📊 Usage updated - randomize used: {success}, new count: {usage_session.randomizes_used}/{usage_session.MAX_RANDOMIZES}")

            return Response({
                "id": temp_image.id,
                "match_name": random_figure,
                "match_score": 1.0,
                "message": f"You've been randomly transformed into {random_figure}!",
                "output_image_url": temp_image.output_image.url,
                "original_selfie_url": temp_image.selfie.url,
                "historical_figure_url": historical_image_url,
                "is_randomized": True,
                "usage": self.get_usage_data(request, usage_session)
            })

        except Exception as e:
            if temp_image:
                try:
                    temp_image.delete()
                except:
                    pass
            return Response({"error": f"Randomized face processing failed: {str(e)}"}, status=500)
        
        finally:
            current_jobs = cache.get('active_face_swap_jobs', 1)
            cache.set('active_face_swap_jobs', max(0, current_jobs - 1), timeout=300)

    def get_usage_data(self, request, usage_session):
        if request.user.is_authenticated:
            return {"unlimited": True}
        elif usage_session:
            return {
                "matches_used": usage_session.matches_used,
                "matches_limit": usage_session.MAX_MATCHES,
                "randomizes_used": usage_session.randomizes_used,
                "randomizes_limit": usage_session.MAX_RANDOMIZES,
                "can_match": usage_session.can_match,
                "can_randomize": usage_session.can_randomize,
                "is_limited": usage_session.is_limited,
            }
        return None


class UsageStatusView(APIView):
    """Get current usage status - FIXED VERSION"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"unlimited": True, "user_authenticated": True})
        
        # 🔥 CRITICAL FIX: Force session creation if it doesn't exist
        if not request.session.session_key:
            request.session.create()
            request.session.save()
            print(f"🔑 Created session in usage status: {request.session.session_key}")
        else:
            print(f"🔑 Using existing session: {request.session.session_key}")
            
        # Get or create usage session
        usage_session = UsageSession.get_or_create_for_session(request.session.session_key)
        print(f"📊 Retrieved usage: matches={usage_session.matches_used}, randomizes={usage_session.randomizes_used}")
        
        return Response({
            "matches_used": usage_session.matches_used,
            "matches_limit": usage_session.MAX_MATCHES,
            "randomizes_used": usage_session.randomizes_used,
            "randomizes_limit": usage_session.MAX_RANDOMIZES,
            "can_match": usage_session.can_match,
            "can_randomize": usage_session.can_randomize,
            "is_limited": usage_session.is_limited,
            "user_authenticated": False,
            "session_key": request.session.session_key[:8] + "...",  # For debugging
        })


# Keep existing views unchanged
class ImageStatusView(APIView):
    def get(self, request, prediction_id):
        try:
            generated_image = GeneratedImage.objects.get(id=prediction_id)
            return Response({
                "id": generated_image.id,
                "status": "completed" if generated_image.output_image else "processing",
                "match_name": generated_image.match_name,
                "prompt": generated_image.prompt,
                "output_image_url": generated_image.output_image.url if generated_image.output_image else None,
                "created_at": generated_image.created_at
            })
        except GeneratedImage.DoesNotExist:
            return Response({"error": "Generated image not found"}, status=404)


class UnlockImageView(APIView):
    def post(self, request):
        request.session["image_generation_count"] = 0
        return Response({"message": "Unlock granted. You can generate again."})


class ListGeneratedImagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
        results = []
        for img in images:
            results.append({
                "id": img.id,
                "match_name": img.match_name,
                "prompt": img.prompt,
                "output_image_url": img.output_image.url if img.output_image else None,
                "selfie_url": img.selfie.url,
                "created_at": img.created_at
            })
        return Response({"images": results})