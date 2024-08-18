<template>
    <div class="construction-page">
        <h1>网站正在建设中</h1>
        <p>我们正在努力建设这个网站，敬请期待！</p>
        <p>请稍后再回来查看更新。</p>
        <div class="loader"></div>
        <a style="text-decoration: none;color: #606266;margin-left: 1rem" target="_blank" :href="ICPurl">赣ICP备2024031666号</a>
    </div>
</template>

<script setup lang="ts">
const ICPurl = "https://beian.miit.gov.cn/";

</script>

<style scoped>
.construction-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    text-align: center;
    background-color: #f0f0f0;
    color: #333;
}
a{
    position: absolute  ;
    bottom: 0;
    left: 0;
    right: 0;
    margin-bottom: 1rem;
    
}

h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

p {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.loader {
    border: 8px solid #f3f3f3;
    border-radius: 50%;
    border-top: 8px solid #333;
    width: 60px;
    height: 60px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}
</style>